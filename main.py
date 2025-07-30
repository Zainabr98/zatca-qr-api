from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import qrcode
import base64
import os
from datetime import datetime
from fastapi.responses import FileResponse

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Model
class InvoiceData(BaseModel):
    sellerName: str
    vatRegistrationNumber: str
    timeStamp: str
    invoiceTotal: str
    vatTotal: str

# Make sure the directory exists
os.makedirs("static/qr_images", exist_ok=True)

@app.post("/generate_qr")
def generate_qr(data: InvoiceData):
    # Construct TLV structure
    def to_tlv(tag, value):
        return bytes([tag]) + bytes([len(value.encode('utf-8'))]) + value.encode('utf-8')

    tlv_bytes = b"".join([
        to_tlv(1, data.sellerName),
        to_tlv(2, data.vatRegistrationNumber),
        to_tlv(3, data.timeStamp),
        to_tlv(4, data.invoiceTotal),
        to_tlv(5, data.vatTotal)
    ])

    base64_tlv = base64.b64encode(tlv_bytes).decode('utf-8')

    # Generate QR
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(base64_tlv)
    qr.make(fit=True)

    img = qr.make_image(fill="black", back_color="white")

    # Save image to static folder
    filename = f"qr_{datetime.utcnow().strftime('%Y%m%d%H%M%S%f')}.png"
    filepath = os.path.join("static", "qr_images", filename)
    img.save(filepath)

    # Construct public URL
    base_url = "https://zatca-qr-api-t0ix.onrender.com"
    qr_code_url = f"{base_url}/static/qr_images/{filename}"

    return {
        "base64_tlv": base64_tlv,
        "qr_code_url": qr_code_url
    }

@app.get("/")
def home():
    return {"message": "ZATCA QR API is running!"}
