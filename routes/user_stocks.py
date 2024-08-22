from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import  get_current_stocks_collection
from models.model import  CurrentStockRecordResponse
from pymongo.collection import Collection

router = APIRouter()

@router.get("/user_stocks",response_model=List[CurrentStockRecordResponse])
async def get_user_stocks( token: str=Depends(get_current_user),
                          user_stocks: Collection = Depends(get_current_stocks_collection)):
    user_stocks_data = user_stocks.find({"owner": token})
    if not user_stocks_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stocks found")
    return [CurrentStockRecordResponse(**stock, id=str(stock["_id"])) for stock in user_stocks_data]

@router.get("/user_stocks/{symbol}",response_model=CurrentStockRecordResponse)
async def get_user_stock(symbol:str,token: str=Depends(get_current_user),
                          user_stocks: Collection = Depends(get_current_stocks_collection)):
    user_stock_data = user_stocks.find_one({"owner": token, "symbol": symbol})
    if not user_stock_data:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stock found")
    return CurrentStockRecordResponse(**user_stock_data, id=str(user_stock_data["_id"]))