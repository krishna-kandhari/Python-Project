from fastapi import APIRouter

router = APIRouter()

@router.post("/login")
async def login(credentials: dict):
    # Dummy mock for google auth integration
    return {"status": "success", "token": "dummy_token_123", "user": {"name": "Test User"}}

@router.get("/me")
async def get_user_profile():
    return {"name": "Test User", "email": "test@example.com"}
