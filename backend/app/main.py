
import os
from fastapi import FastAPI, UploadFile, File, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from fastapi_jwt_auth import AuthJWT
from fastapi_jwt_auth.exceptions import AuthJWTException
from pydantic import BaseModel
import uuid, csv
from dotenv import load_dotenv
load_dotenv()

class Settings(BaseModel):
    authjwt_secret_key: str = os.getenv("JWT_SECRET_KEY", "super-secret")

@AuthJWT.load_config
def get_config():
    return Settings()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.exception_handler(AuthJWTException)
def auth_exception_handler(request: Request, exc: AuthJWTException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.message})

@app.get("/")
def root():
    return {"status": "ok", "service": "saicas-backend"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return [{"nome": "P1", "materiale": "S235JR", "spessore": 3, "lavorazioni": ["taglio laser", "piegatura"], "trattamenti": ["verniciatura a polvere"]}]

@app.post("/quote/calculate")
async def calculate_quote(items: list[dict], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    return {"totale_commessa": 100.0}

@app.post("/quote/export")
async def export_csv(items: list[dict], Authorize: AuthJWT = Depends()):
    Authorize.jwt_required()
    temp_id = str(uuid.uuid4())
    path = f"./{temp_id}.csv"
    with open(path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=items[0].keys())
        writer.writeheader()
        for item in items:
            writer.writerow(item)
    return FileResponse(path, filename="preventivo.csv", media_type="text/csv")
