
from flask import Flask, request, jsonify
import base64
import qrcode
from io import BytesIO

app = Flask(__name__)

def encode_tlv(tag, value):
    value_bytes = value.encode('utf-8')
    return bytes([tag]) + bytes([len(value_bytes)]) + value_bytes

@app.route('/generate_qr', methods=['POST'])
def generate_qr():
    data = request.json
    try:
        tlv = b''.join([
            encode_tlv(1, data['sellerName']),
            encode_tlv(2, data['vatRegistrationNumber']),
            encode_tlv(3, data['timeStamp']),
            encode_tlv(4, data['invoiceTotal']),
            encode_tlv(5, data['vatTotal']),
        ])
        b64_tlv = base64.b64encode(tlv).decode('utf-8')

        img = qrcode.make(b64_tlv)
        buffer = BytesIO()
        img.save(buffer, format="PNG")
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return jsonify({
            "base64_tlv": b64_tlv,
            "qr_code_image": f"data:image/png;base64,{img_base64}"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run()
