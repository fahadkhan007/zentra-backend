import logging

# Configure a named logger so RAG activity always shows in the terminal
logger = logging.getLogger("zentra.rag")
logger.setLevel(logging.INFO)
if not logger.handlers:
    _handler = logging.StreamHandler()
    _handler.setFormatter(
        logging.Formatter("%(asctime)s | %(levelname)s | %(name)s | %(message)s", datefmt="%H:%M:%S")
    )
    logger.addHandler(_handler)
from langgraph.prebuilt import create_react_agent
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.tools import create_retriever_tool
from langchain_core.messages import AIMessage, HumanMessage
from app.rag.vector_store import retriever
from app.core.config import settings

llm = ChatGoogleGenerativeAI(
    model="gemini-2.5-flash-lite",
    google_api_key=settings.GEMINI_API_KEY,
    temperature=0.7,
)

retriever_tool = create_retriever_tool(
    retriever=retriever,
    name="fitness_knowledge",
    description="Search the fitness knowledge base for information about exercises, workout plans, nutrition, and health advice. Always use this tool to retrieve relevant information before answering any fitness, health, or nutrition related question.",
)

AGENT_SYSTEM_PROMPT = """You are a knowledgeable fitness and health assistant.

IMPORTANT: You MUST always use the fitness_knowledge tool to search the knowledge base before answering ANY question related to fitness, exercise, nutrition, health, or wellness — even if you think you already know the answer. Always retrieve relevant documents first, then use them to formulate your response.

Only skip the tool if the question is completely unrelated to health or fitness."""

agent = create_react_agent(
    model=llm,
    tools=[retriever_tool],
    prompt=AGENT_SYSTEM_PROMPT,
)

print("✅ RAG agent initialized")


async def chat(
    session_id: str, message: str, history: list = None, user_profile=None
) -> str:
    """
    Chat with RAG agent, injecting user health profile as context.

    Args:
        session_id: Unique session identifier
        message: User's message
        history: Previous conversation history
        user_profile: UserHealthProfile object with user's health data
    """
    from langchain_core.messages import SystemMessage

    # Always prepend agent system prompt to enforce tool usage
    messages = [SystemMessage(content=AGENT_SYSTEM_PROMPT)]

    # Inject user profile as system context if available
    if user_profile:
        profile_context = f"""User Profile Information:
 - Gender: {user_profile.gender or "Not specified"}
- Age: {user_profile.age or "Not specified"}
- Height: {user_profile.height_m}m, Weight: {user_profile.weight_kg}kg, BMI: {user_profile.bmi}
- Physical Activity: {user_profile.physical_activity_hours or 0} hours/day
- Main Meals: {user_profile.main_meals_per_day or "Not specified"} per day
- Water Intake: {user_profile.water_intake_liters or "Not specified"} liters/day
- Screen Time: {user_profile.screentime_hours or "Not specified"} hours/day
- Vegetable Intake Frequency: {user_profile.vegetable_intake_freq or "Not specified"}
- Snack Frequency: {user_profile.snack_frequency or "Not specified"}
- High Calorie Food Consumption: {user_profile.high_calorie_food or "Not specified"}
- Smoking: {user_profile.smokes or "Not specified"}
- Alcohol: {user_profile.alcohol_consumption or "Not specified"}
- Travel Mode: {user_profile.travel_mode or "Not specified"}
- Calorie Tracking: {user_profile.calorie_tracking or "Not specified"}

Use this information to provide personalized fitness and nutrition advice. Don't ask for information that's already provided above."""

        messages.append(SystemMessage(content=profile_context))

    # Add conversation history
    if history:
        for msg in history:
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    # Add current user message
    messages.append(HumanMessage(content=message))

    # ── RAG invocation ───────────────────────────────────────────────────────
    logger.info("⏳ [RAG] Invoking agent for session: %s | query: %.80s", session_id, message)

    result = await agent.ainvoke({"messages": messages})

    # ── Inspect which tools were called and what was retrieved ────────────────
    from langchain_core.messages import ToolMessage

    tool_messages = [m for m in result["messages"] if isinstance(m, ToolMessage)]
    tools_called  = [m.name for m in tool_messages]

    if tool_messages:
        logger.info("✅ [RAG] Vector DB WAS queried — tools called: %s", tools_called)
        for tm in tool_messages:
            # Each ToolMessage content is the raw retrieved docs as a string
            doc_snippets = tm.content if isinstance(tm.content, str) else str(tm.content)
            num_chars = len(doc_snippets)
            logger.info(
                "📄 [RAG] Retrieved %d chars of context from '%s'",
                num_chars,
                tm.name,
            )
            # Print first 300 chars of each retrieved chunk so you can verify relevance
            logger.info("📝 [RAG] Context preview: %s...", doc_snippets[:300].replace("\n", " "))
    else:
        logger.warning(
            "⚠️  [RAG] Vector DB was NOT queried — Gemini answered from training data! "
            "Check the system prompt or tool binding."
        )

    return result["messages"][-1].content
