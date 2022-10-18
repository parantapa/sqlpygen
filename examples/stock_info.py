from pydantic import BaseModel

class StockInfo(BaseModel):
    volume: float
