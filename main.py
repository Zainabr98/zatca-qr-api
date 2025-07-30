from fastapi import FastAPI
from pydantic import BaseModel
import qrcode
import base64
from io import BytesIO
from datetime import datetime
from fastapi.responses import JSONResponse
import cloudinary
import cloudinary.uploader

# إعداد Cloudinary
cloudinary.config(
    cloud_name="dprycvrhz",
    api_key="426522214543791",
    api_secret="m2fv1N33PtKaBMjV25At0C1aUQM"
)

app = FastAPI()

class QRRequest(BaseModel):
    sellerName: str
    vatRegistrationNumber: str
    timeStamp: str
    invoiceTotal: str
    vatTotal: str

@app.post("/generate_qr")
async def generate_qr(data: QRRequest):
    try:
        # توليد TLV (Tag-Length-Value)
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

        # توليد QR كصورة
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(base64_tlv)
        qr.make(fit=True)
        img = qr.make_image(fill='black', back_color='white')

        # تحويل الصورة إلى BytesIO
        img_buffer = BytesIO()
        img.save(img_buffer, format="PNG")
        img_buffer.seek(0)

        # رفع الصورة إلى Cloudinary
        public_id = f"qr_{datetime.now().strftime('%Y%m%d%H%M%S%f')}"
        result = cloudinary.uploader.upload(img_buffer, public_id=public_id, folder="zatca_qr")

        # رابط الصورة
        image_url = result.get("secure_url")
        return JSONResponse({"qr_code_url": image_url})

    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
