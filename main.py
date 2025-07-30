from fastapi import FastAPI, Request
from pydantic import BaseModel
import qrcode
import base64
from io import BytesIO
import os
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

# Serve static files (QR images)
app.mount("/static", StaticFiles(directory="static"), name="static")

# Ensure folder exists
os.makedirs("static/qr_images", exist_ok=True)

class QRRequest(BaseModel):
    sellerName: str
    vatRegistrationNumber: str
    timeStamp: str
    invoiceTotal: str
    vatTotal: str

@app.post("/generate_qr")
async def generate_qr(data: QRRequest):
    try:
        # Generate the TLV (Tag-Length-Value) structure
        def to_tlv(tag, value):
            value_bytes = value.encode('utf-8')
            return bytes([tag]) + bytes([len(value_bytes)]) + value_bytes

        tlv_bytes = (
            to_tlv(1, data.sellerName) +
            to_tlv(2, data.vatRegistrationNumber) +
            to_tlv(3, data.timeStamp) +
            to_tlv(4, data.invoiceTotal) +
            to_tlv(5, data.vatTotal)
        )

        base64_tlv = base64.b64encode(tlv_bytes).decode('utf-8')

        # Generate QR code
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(base64_tlv)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # Save QR image to static/qr_images with unique name
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S%f")
        filename = f"qr_{timestamp}.png"
        filepath = os.path.join("static", "qr_images", filename)
        img.save(filepath)

        image_url = f"https://zatca-qr-api-t0ix.onrender.com/static/qr_images/{filename}"

        return JSONResponse({"qr_code_url": image_url})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
