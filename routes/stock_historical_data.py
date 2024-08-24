from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
import pandas as pd
import yfinance as yf
from auth.auth import get_current_user
from database.database import (
    get_purchase_collection,
    get_sold_collection,
    get_stock_data_collection,
    get_current_stocks_collection,
)
from bson import ObjectId
from datetime import datetime, timedelta
from models.model import (
    SoldRecordResponse,
    CurrentStockRecordResponse,
    PurchaseRecordResponse,
    StockResponse,
)
from pymongo.collection import Collection
import json
import os

file_path = r"E:\all together website\historical and live data fro stocks\backend_for_notes_expense_stocks\routes\symbols_results.xlsx"
if not os.path.exists(file_path):
    raise FileNotFoundError(f"The file {file_path} does not exist.")
valid_symbols = pd.read_excel(file_path, sheet_name="Valid Symbols")[
    "Valid Symbols"
].tolist()


router = APIRouter()


@router.get("/all_stocks_data_of_users/{symbol}", response_model=dict)
async def get_all_stocks_data_of_user(
    symbol: str,
    token: str = Depends(get_current_user),
    current_stocks_collection: Collection = Depends(get_current_stocks_collection),
    purchases_collection: Collection = Depends(get_purchase_collection),
    sold_collection: Collection = Depends(get_sold_collection),
):
    solds_stock = sold_collection.find({"owner": token, "symbol": symbol})
    if not solds_stock:
        sold_record = []
    else:
        sold_record = [
            SoldRecordResponse(**sold, id=str(sold["_id"])) for sold in solds_stock
        ]
    buy_stock = purchases_collection.find({"owner": token, "symbol": symbol})
    if not buy_stock:
        buy_record = []
    else:
        buy_record = [
            PurchaseRecordResponse(**purchase, id=str(purchase["_id"]))
            for purchase in buy_stock
        ]
    current_stock = current_stocks_collection.find_one(
        {"owner": token, "symbol": symbol}
    )
    if not current_stock:
        current_stock_record = []
    else:
        current_stock_record = CurrentStockRecordResponse(
            **current_stock, id=str(current_stock["_id"])
        )
    return {
        "sold_records": sold_record,
        "buy_stock": buy_record,
        "current_stock": current_stock_record,
    }
@router.get("/fetch_historical_last_month_data/{symbol}", response_model=dict)
async def fetch_historical_last_month_data(symbol:str):
    symbol = symbol.upper()
    symbol = symbol + ".NS"
    if symbol not in valid_symbols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol"
        )
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    data = yf.download(symbol, start=start_date_str, end=end_date_str, interval="5m")
    df = pd.DataFrame(data)
    last_month_data = [
        {
            "Date": date.strftime("%Y-%m-%d"),
            "Time": date.strftime("%H:%M:%S"),
            "Close": round(float(row["Close"]), 3),
            "Volume": int(row["Volume"]),
        }
        for date, row in df.iterrows()
    ]
    return {"last_month_data":last_month_data}
@router.get("/fetch_historical_last_week_data/{symbol}", response_model=dict)
async def fetch_historical_last_week_data(symbol:str):
    symbol = symbol.upper()
    symbol = symbol + ".NS"
    if symbol not in valid_symbols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol"
        )
    end_date = datetime.now()
    start_date = end_date - timedelta(days=7)
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    data = yf.download(symbol, start=start_date_str, end=end_date_str, interval="5m")
    df = pd.DataFrame(data)
    last_week_data = [
        {
            "Date": date.strftime("%Y-%m-%d"),
            "Time": date.strftime("%H:%M:%S"),
            "Close": round(float(row["Close"]), 3),
            "Volume": int(row["Volume"]),
        }
        for date, row in df.iterrows()
    ]
    return {"last_week_data":last_week_data}
@router.get("/fetch_historical_last_day_data/{symbol}", response_model=dict)
async def fetch_historical_last_day_data(symbol:str):
    symbol = symbol.upper()
    symbol = symbol + ".NS"
    if symbol not in valid_symbols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol"
        )
    data = yf.download(symbol, period="1d", interval="5m")
    df = pd.DataFrame(data)
    last_day_data = [
        {
            "Date": date.strftime("%Y-%m-%d"),
            "Time": date.strftime("%H:%M:%S"),
            "Close": round(float(row["Close"]), 3),
            "Volume": int(row["Volume"]),
        }
        for date, row in df.iterrows()
    ]
    return {"last_dau_data":last_day_data}
@router.get("/fetch_historical_data_of_the_symbol/{symbol}", response_model=dict)
async def fetch_historical_data_of_the_symbol(symbol: str):
    symbol = symbol.upper()
    symbol = symbol + ".NS"
    if symbol not in valid_symbols:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol"
        )
    data = yf.download(symbol, start="1950-01-01", end=None)
    df = pd.DataFrame(data)
    all_historical_data = [
        {
            "Date": date.strftime("%Y-%m-%d"),
            "Close": round(float(row["Close"]), 3),
            "Volume": int(row["Volume"]),
        }
        for date, row in df.iterrows()
    ]
    return {
        "historical_data": all_historical_data,
    }
