from fastapi import APIRouter

router = APIRouter()

@router.post("/start_walk")
async def start_walk(data: dict):
    return {"status": "success", "session_id": "walk_123"}

@router.post("/start_ride")
async def start_ride(data: dict):
    return {"status": "success", "session_id": "ride_123"}

@router.post("/update_location")
async def update_location(data: dict):
    # This would check deviation logic
    return {"status": "success", "deviation": False}
