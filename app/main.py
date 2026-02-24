from starlette.responses import HTMLResponse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from scalar_fastapi.scalar_fastapi import get_scalar_api_reference
from contextlib import asynccontextmanager

from app.api.auth_router import router as auth_router  # type: ignore
from app.api.prediction_router import router as prediction_router  # type: ignore
from app.api.profile_router import router as profile_router  # type: ignore
from app.api.chat_router import router as chat_router  # type: ignore
from app.db.database import Base, engine  # type: ignore


@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    import app.rag.vector_store
    import app.rag.rag_chain

    yield
    await engine.dispose()


description = """
Zentra is a high-performance intelligent backend providing secure authentication, 
user profile management, and advanced prediction capabilities with generative ai assistant for heath and wellness.
"""


app = FastAPI(
    lifespan=lifespan,
    title="Zentra API",
    description=description,
    version="1.0.0",
    docs_url=None,
    redoc_url=None,
    generate_unique_id_function=lambda route: route.name,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",  
        "http://localhost:3000", 
        "https://zentra-ai.up.railway.app", 
        "https://zentra-ai-app.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(profile_router)
app.include_router(prediction_router)
app.include_router(chat_router)


@app.get("/", include_in_schema=False)
def root():
    return HTMLResponse("""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Zentra API</title>
        <script src="https://cdn.tailwindcss.com"></script>
    </head>
    <body class="bg-gray-950 text-gray-100 font-sans min-h-screen flex items-center justify-center">
        <div class="max-w-2xl p-12 bg-gray-900 rounded-3xl shadow-2xl border border-gray-800 text-center">
            <h1 class="text-5xl font-black mb-6 bg-gradient-to-br from-blue-400 via-indigo-500 to-purple-600 bg-clip-text text-transparent leading-tight">
                Zentra API
            </h1>
            <p class="text-gray-400 text-lg mb-10 leading-relaxed">
                A high-performance intelligent backend providing secure authentication, 
                user profile management, and advanced prediction capabilities.
            </p>
            <div class="grid grid-cols-1 md:grid-cols-3 gap-4 mb-10 text-left">
                <div class="p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
                    <div class="text-blue-400 font-bold mb-1">Auth</div>
                    <p class="text-xs text-gray-500">JWT-based secure access control.</p>
                </div>
                <div class="p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
                    <div class="text-indigo-400 font-bold mb-1">Profiles</div>
                    <p class="text-xs text-gray-500">Comprehensive user data storage.</p>
                </div>
                <div class="p-4 bg-gray-800/50 rounded-xl border border-gray-700/50">
                    <div class="text-purple-400 font-bold mb-1">Predictions</div>
                    <p class="text-xs text-gray-500">Scalable ML model inference.</p>
                </div>
            </div>
            <div class="flex flex-wrap gap-4 justify-center">
                <a href="/docs" class="px-8 py-3 bg-blue-600 hover:bg-blue-500 text-white rounded-full font-semibold transition-all shadow-lg shadow-blue-900/20">
                    Swagger Docs
                </a>
                <a href="/scalar" class="px-8 py-3 bg-gray-800 hover:bg-gray-700 text-white rounded-full font-semibold transition-all border border-gray-700">
                    Scalar Reference
                </a>
            </div>
        </div>
    </body>
    </html>
    """)


@app.get("/scalar", include_in_schema=False)
def get_scalar_api():
    return get_scalar_api_reference(openapi_url=app.openapi_url, title="scalar docs")
