from fastapi import APIRouter

router = APIRouter()

@router.post("/set_checkin")
async def set_checkin(data: dict):
    # Expecting eta in mins
    return {"status": "success", "message": "Check-in timer started"}

@router.post("/confirm_checkin")
async def confirm_checkin(data: dict):
    return {"status": "success", "message": "Arrived safely"}
