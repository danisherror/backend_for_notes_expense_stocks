from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import get_current_stocks_collection
from models.model import CurrentStockRecordResponse
from pymongo.collection import Collection

class UserStocksRouter:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        self.router.add_api_route("/user_stocks", self.get_user_stocks, methods=["GET"], response_model=List[CurrentStockRecordResponse])
        self.router.add_api_route("/user_stocks/{symbol}", self.get_user_stock, methods=["GET"], response_model=CurrentStockRecordResponse)

    async def get_user_stocks(self, 
                               token: str = Depends(get_current_user), 
                               user_stocks: Collection = Depends(get_current_stocks_collection)):
        user_stocks_data = user_stocks.find({"owner": token})
        if user_stocks_data.count() == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stocks found")
        return [CurrentStockRecordResponse(**stock, id=str(stock["_id"])) for stock in user_stocks_data]

    async def get_user_stock(self, symbol: str, 
                              token: str = Depends(get_current_user), 
                              user_stocks: Collection = Depends(get_current_stocks_collection)):
        user_stock_data = user_stocks.find_one({"owner": token, "symbol": symbol})
        if not user_stock_data:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No stock found")
        return CurrentStockRecordResponse(**user_stock_data, id=str(user_stock_data["_id"]))

# Instantiate and register the UserStocksRouter
user_stocks_router_instance = UserStocksRouter()
router = user_stocks_router_instance.router
