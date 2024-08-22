from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import  get_current_user
from database.database import get_purchase_collection, get_sold_collection, get_stock_data_collection, get_current_stocks_collection
from bson import ObjectId
from datetime import datetime
from models.model import SoldRecordResponse, CurrentStockRecordResponse, PurchaseRecordResponse,StockResponse
from pymongo.collection import Collection

router = APIRouter()

@router.get("/all_stocks_data_of_users/{symbol}",response_model=dict)
async def get_all_stocks_data_of_user(symbol: str, token: str= Depends(get_current_user),
                                       stock_data_collection: Collection = Depends(get_stock_data_collection),
                                       current_stocks_collection: Collection = Depends(get_current_stocks_collection),
                                       purchases_collection: Collection = Depends(get_purchase_collection),
                                       sold_collection: Collection = Depends(get_sold_collection)):
    solds_stock= sold_collection.find({"owner":token,"symbol":symbol})
    if not solds_stock:
        sold_record=[]
    else:
        sold_record= [SoldRecordResponse(**sold,id=str(sold["_id"])) for sold in solds_stock]
    buy_stock= purchases_collection.find({"owner":token,"symbol":symbol})
    if not buy_stock:
        buy_record=[]
    else:
        buy_record= [PurchaseRecordResponse(**purchase,id=str(purchase["_id"])) for purchase in buy_stock]
    current_stock=current_stocks_collection.find_one({"owner":token,"symbol":symbol})
    if not current_stock:
        current_stock_record=[]
    else:
        current_stock_record=CurrentStockRecordResponse(**current_stock,id=str(current_stock["_id"]))
    ################
    # send historical data of that stock
    ################
    return {"sold_records":sold_record,
            "buy_stock":buy_record,
            "current_stock":current_stock_record}

@router.get("/stock_update_all_historical_live_data")
async def stock_update_all_historical_live_data(stock_data: Collection=Depends(get_stock_data_collection)):
    pass

@router.get("/all_stock_datas/{symbol}",response_model=StockResponse)
async def all_stock_datas(symbol: str,stock_data: Collection=Depends(get_stock_data_collection) ):
    stock_data_cursor= stock_data.find({"symbol":symbol})
    if not stock_data_cursor:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stock data found")
    return StockResponse(**stock_data_cursor,id=str(stock_data_cursor["_id"]))
