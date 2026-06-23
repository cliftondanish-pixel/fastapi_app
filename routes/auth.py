from fastapi import APIRouter

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.get("/")
def auth_test():
    return {"message": "Auth Route Working"}