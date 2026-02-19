from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, desc
from uuid import UUID

from app.db.database import get_db
from app.db.models import User, ChatSession, ChatMessage, UserHealthProfile
from app.schemas.chat import (
    ChatRequest,
    ChatResponse,
    ChatMessageResponse,
    ChatSessionSummary,
    ChatSessionDetail,
    ChatSessionListResponse,
    UpdateSessionTitleRequest,
)
from app.api.auth_router import get_current_user
from app.rag import chat as rag_chat

router = APIRouter(prefix="/chat", tags=["Chat"])


@router.post(
    "/sessions", response_model=ChatSessionSummary, status_code=status.HTTP_201_CREATED
)
async def create_session(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    new_session = ChatSession(user_id=current_user.id, title="New Chat")
    db.add(new_session)
    await db.commit()
    await db.refresh(new_session)

    return ChatSessionSummary(
        id=new_session.id,
        title=new_session.title,
        created_at=new_session.created_at,
        updated_at=new_session.updated_at,
        message_count=0,
    )


@router.get("/sessions", response_model=ChatSessionListResponse)
async def list_sessions(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession)
        .where(ChatSession.user_id == current_user.id)
        .order_by(desc(ChatSession.updated_at))
    )
    sessions = result.scalars().all()

    session_summaries = []
    for session in sessions:
        count_result = await db.execute(
            select(func.count(ChatMessage.id)).where(
                ChatMessage.session_id == session.id
            )
        )
        message_count = count_result.scalar()

        session_summaries.append(
            ChatSessionSummary(
                id=session.id,
                title=session.title,
                created_at=session.created_at,
                updated_at=session.updated_at,
                message_count=message_count,
            )
        )

    return ChatSessionListResponse(
        sessions=session_summaries, total=len(session_summaries)
    )


@router.get("/sessions/{session_id}", response_model=ChatSessionDetail)
async def get_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    messages = messages_result.scalars().all()

    message_responses = [
        ChatMessageResponse(
            id=msg.id,
            role=msg.role,
            content=msg.content,
            sources=None,
            created_at=msg.created_at,
        )
        for msg in messages
    ]

    return ChatSessionDetail(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        messages=message_responses,
    )


@router.post("/sessions/{session_id}/messages", response_model=ChatResponse)
async def send_message(
    session_id: UUID,
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    # Fetch user health profile
    profile_result = await db.execute(
        select(UserHealthProfile).where(UserHealthProfile.user_id == current_user.id)
    )
    user_profile = profile_result.scalar_one_or_none()

    user_message = ChatMessage(
        session_id=session_id, role="user", content=request.message, sources=None
    )
    db.add(user_message)
    await db.commit()

    messages_result = await db.execute(
        select(ChatMessage)
        .where(ChatMessage.session_id == session_id)
        .order_by(ChatMessage.created_at)
    )
    history = [
        {"role": msg.role, "content": msg.content}
        for msg in messages_result.scalars().all()
    ]

    ai_response = await rag_chat(
        session_id=str(session_id),
        message=request.message,
        history=history[:-1],
        user_profile=user_profile,
    )

    ai_message = ChatMessage(
        session_id=session_id, role="assistant", content=ai_response, sources=None
    )
    db.add(ai_message)
    await db.commit()
    await db.refresh(ai_message)

    return ChatResponse(
        message=ChatMessageResponse(
            id=ai_message.id,
            role=ai_message.role,
            content=ai_message.content,
            sources=None,
            created_at=ai_message.created_at,
        ),
        session_id=session_id,
    )


@router.patch("/sessions/{session_id}/title", response_model=ChatSessionSummary)
async def update_session_title(
    session_id: UUID,
    request: UpdateSessionTitleRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    session.title = request.title
    await db.commit()
    await db.refresh(session)

    count_result = await db.execute(
        select(func.count(ChatMessage.id)).where(ChatMessage.session_id == session_id)
    )
    message_count = count_result.scalar()

    return ChatSessionSummary(
        id=session.id,
        title=session.title,
        created_at=session.created_at,
        updated_at=session.updated_at,
        message_count=message_count,
    )


@router.delete("/sessions/{session_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_session(
    session_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ChatSession).where(
            ChatSession.id == session_id, ChatSession.user_id == current_user.id
        )
    )
    session = result.scalar_one_or_none()

    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    await db.delete(session)
    await db.commit()

    return {
        "message":"session deleted successfully"
    }
