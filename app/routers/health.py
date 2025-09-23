
from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "Tree analysis server is running"}

@router.get("/")
async def root():
    return {"message": "Health router is working"}
