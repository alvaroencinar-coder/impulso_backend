from fastapi import APIRouter

router = APIRouter()

@router.get("/status")
async def status():
    return {"status": "Ruta /app/routes/decision.py activa y funcionando correctamente"}
