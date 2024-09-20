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
)
from pymongo.collection import Collection

class StockRouter:
    def __init__(self):
        self.router = APIRouter()
        self.valid_symbols = pd.read_excel('./routes/symbols_results.xlsx', sheet_name="Valid Symbols")["Valid Symbols"].tolist()
        self.setup_routes()

    def setup_routes(self):
        self.router.add_api_route("/all_stocks_data_of_users/{symbol}", self.get_all_stocks_data_of_user, methods=["GET"])
        self.router.add_api_route("/fetch_historical_last_month_data/{symbol}", self.fetch_historical_last_month_data, methods=["GET"])
        self.router.add_api_route("/fetch_historical_last_week_data/{symbol}", self.fetch_historical_last_week_data, methods=["GET"])
        self.router.add_api_route("/fetch_historical_last_day_data/{symbol}", self.fetch_historical_last_day_data, methods=["GET"])
        self.router.add_api_route("/fetch_historical_data_of_the_symbol/{symbol}", self.fetch_historical_data_of_the_symbol, methods=["GET"])
        self.router.add_api_route("/all_stocks_names", self.get_all_stocks_names, methods=["GET"])

    async def get_all_stocks_data_of_user(self, symbol: str, token: str = Depends(get_current_user), 
                                           current_stocks_collection: Collection = Depends(get_current_stocks_collection),
                                           purchases_collection: Collection = Depends(get_purchase_collection),
                                           sold_collection: Collection = Depends(get_sold_collection)):
        solds_stock = sold_collection.find({"owner": token, "symbol": symbol})
        sold_record = [SoldRecordResponse(**sold, id=str(sold["_id"])) for sold in solds_stock] if solds_stock else []

        buy_stock = purchases_collection.find({"owner": token, "symbol": symbol})
        buy_record = [PurchaseRecordResponse(**purchase, id=str(purchase["_id"])) for purchase in buy_stock] if buy_stock else []

        current_stock = current_stocks_collection.find_one({"owner": token, "symbol": symbol})
        current_stock_record = CurrentStockRecordResponse(**current_stock, id=str(current_stock["_id"])) if current_stock else []

        return {
            "sold_records": sold_record,
            "buy_stock": buy_record,
            "current_stock": current_stock_record,
        }

    async def fetch_historical_last_month_data(self, symbol: str):
        return await self.fetch_historical_data(symbol, days=30)

    async def fetch_historical_last_week_data(self, symbol: str):
        return await self.fetch_historical_data(symbol, days=7)

    async def fetch_historical_last_day_data(self, symbol: str):
        return await self.fetch_historical_data(symbol, days=1)

    async def fetch_historical_data(self, symbol: str, days: int):
        symbol = symbol.upper() + ".NS"
        if symbol not in self.valid_symbols:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol")

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        data = yf.download(symbol, start=start_date.strftime("%Y-%m-%d"), end=end_date.strftime("%Y-%m-%d"), interval="5m")
        if data.empty:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No data found for the given symbol")

        df = pd.DataFrame(data)
        historical_data = [
            {
                "Date": date.strftime("%Y-%m-%d %I:%M %p"),
                "Close": round(float(row["Close"]), 3),
                "Volume": int(row["Volume"]),
            }
            for date, row in df.iterrows()
        ]
        return {"historical_data": historical_data}

    async def fetch_historical_data_of_the_symbol(self, symbol: str):
        symbol = symbol.upper() + ".NS"
        if symbol not in self.valid_symbols:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invalid stock symbol")

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
        return {"historical_data": all_historical_data}

    async def get_all_stocks_names(self):
        symbols = [x.split('.')[0] for x in self.valid_symbols]
        return {"symbols": symbols}

# Instantiate and register the StockRouter
stock_router_instance = StockRouter()
router = stock_router_instance.router
