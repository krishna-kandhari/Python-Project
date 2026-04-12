from fastapi import APIRouter

router = APIRouter()

@router.post("/sos")
async def trigger_sos(location: dict):
    # This will integrate WhatsApp sending eventually
    print("SOS Triggered at", location)
    return {"status": "success", "message": "SOS alert processed"}
