from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
def get_health():
    return {
        "status": "ok",
        "service": "3d-ulpin-backend",
        "version": "1.0.0"
    }
