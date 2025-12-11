# main.py（Vercel 兼容版）
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyproj import Transformer
from typing import List
import json

app = FastAPI()

class ConvertRequest(BaseModel):
    coords: List[List[float]]
    transform: str

@app.post("/convert")
async def convert_coords(request: ConvertRequest):
    try:
        if request.transform == "wgs84_to_cgcs2000":
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:4547", always_xy=True)
            result = []
            for lat, lon in request.coords:
                x, y = transformer.transform(lon, lat)
                result.append([round(x, 6), round(y, 6)])
            return {"result": result}
        elif request.transform == "cgcs2000_to_wgs84":
            transformer = Transformer.from_crs("EPSG:4547", "EPSG:4326", always_xy=True)
            result = []
            for x, y in request.coords:
                lon, lat = transformer.transform(x, y)
                result.append([round(lat, 8), round(lon, 8)])
            return {"result": result}
        else:
            return JSONResponse(status_code=400, content={"error": "仅支持: wgs84_to_cgcs2000 或 cgcs2000_to_wgs84"})
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

# ===== Vercel 入口点 =====
def handler(request):
    from fastapi.middleware.wsgi import WSGIMiddleware
    from starlette.applications import Starlette
    from starlette.routing import Route
    from starlette.requests import Request
    import uvicorn
    from uvicorn.config import Config
    from uvicorn.server import Server
    import asyncio

    # 将 FastAPI 应用包装为 WSGI 应用
    import os
    if os.environ.get("VERCEL"):
        from mangum import Mangum
        return Mangum(app)(request)
    else:
        return app
