from fastapi import FastAPI
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from pyproj import Transformer
from typing import List

app = FastAPI(title="CGCS2000 坐标转换 API")

class ConvertRequest(BaseModel):
    coords: List[List[float]]  # [[lat, lon], ...] 或 [[x, y], ...]
    transform: str             # "wgs84_to_cgcs2000" 或 "cgcs2000_to_wgs84"

@app.post("/convert")
async def convert_coords(request: ConvertRequest):
    try:
        if request.transform == "wgs84_to_cgcs2000":
            transformer = Transformer.from_crs("EPSG:4326", "EPSG:4547", always_xy=True)
            result = []
            for lat, lon in request.coords:
                x, y = transformer.transform(lon, lat)  # 注意：pyproj 用 (lon, lat)
                result.append([round(x, 6), round(y, 6)])  # [x=北向, y=东向]
            return {"result": result}
        
        elif request.transform == "cgcs2000_to_wgs84":
            transformer = Transformer.from_crs("EPSG:4547", "EPSG:4326", always_xy=True)
            result = []
            for x, y in request.coords:
                lon, lat = transformer.transform(x, y)
                result.append([round(lat, 8), round(lon, 8)])  # [lat, lon]
            return {"result": result}
        
        else:
            return JSONResponse(status_code=400, content={"error": "仅支持: wgs84_to_cgcs2000 或 cgcs2000_to_wgs84"})
    
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
