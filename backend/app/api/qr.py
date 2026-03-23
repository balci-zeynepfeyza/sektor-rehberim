from __future__ import annotations

import io

import qrcode
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import Response
from qrcode.constants import ERROR_CORRECT_H


router = APIRouter()


@router.get("/qr")
async def get_qr_png(data: str = Query(..., min_length=1, max_length=2000)) -> Response:
    if not data or not data.strip():
        raise HTTPException(status_code=400, detail="data must be non-empty")

    try:
        qr = qrcode.QRCode(
            version=None,
            error_correction=ERROR_CORRECT_H,
            box_size=10,
            border=4,
        )
        qr.add_data(data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buf = io.BytesIO()
        img.save(buf, format="PNG")
        return Response(content=buf.getvalue(), media_type="image/png")
    except Exception:
        raise HTTPException(status_code=500, detail="Failed to generate QR")

