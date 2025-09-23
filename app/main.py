
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import analysis, health

app = FastAPI(
    title="Tree Analysis API",
    description="API для анализа состояния зеленых насаждений",
    version="1.0.0"
)

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключение роутеров
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(analysis.router, prefix="/api/v1", tags=["analysis"])

@app.get("/")
async def root():
    return {
        "message": "Tree Analysis API Server", 
        "status": "running",
        "docs": "/docs",
        "health": "/api/v1/health"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Server is running"}
