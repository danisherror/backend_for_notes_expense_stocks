from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import get_sold_collection, get_current_stocks_collection
from models.model import SoldRecordCreate, SoldRecordResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

class SoldStocksController:
    def __init__(self):
        self.router = APIRouter()

        # Register the routes
        self.router.post("/sell_stocks")(self.create_sold_record)
        self.router.get("/sell_stocks", response_model=List[SoldRecordResponse])(self.get_sold_records)
        self.router.get("/sell_stocks/{sold_id}", response_model=SoldRecordResponse)(self.get_sold_record)
        self.router.put("/sell_stocks/{sold_id}", response_model=SoldRecordResponse)(self.update_sold_record)
        self.router.delete("/sell_stocks/{sold_id}", response_model=dict)(self.delete_sold_record)

    async def create_sold_record(
        self,
        sold: SoldRecordCreate,
        token: str = Depends(get_current_user),
        get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
        get_sold_collection: Collection = Depends(get_sold_collection),
    ):
        purchase = get_current_stocks_collection.find_one({"symbol": sold.symbol, "owner": token})
        if not purchase:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No purchase record found")

        remaining_quantity = purchase["quantity"] - sold.quantity
        if remaining_quantity < 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stocks to sell")

        prev_net_profit = purchase.get("net_profit", 0.0)
        net_profit = float(sold.price_per_unit_sold) * float(sold.quantity)
        new_net_profit = net_profit + prev_net_profit

        get_current_stocks_collection.update_one(
            {"_id": ObjectId(purchase["_id"])},
            {
                "$set": {
                    "quantity": remaining_quantity,
                    "net_profit": new_net_profit,
                    "last_modified_at": datetime.utcnow(),
                }
            },
        )

        sold_data = sold.dict()
        sold_data["owner"] = token
        result = get_sold_collection.insert_one(sold_data)
        if not result:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create sold record")
        return SoldRecordResponse(**sold_data, id=str(result.inserted_id))

    async def get_sold_records(
        self,
        token: str = Depends(get_current_user),
        get_sold_collection: Collection = Depends(get_sold_collection),
    ):
        solds = get_sold_collection.find({"owner": token})
        if not solds:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found")
        return [SoldRecordResponse(**sold, id=str(sold["_id"])) for sold in solds]

    async def get_sold_record(
        self,
        sold_id: str,
        token: str = Depends(get_current_user),
        get_sold_collection: Collection = Depends(get_sold_collection),
    ):
        sold = get_sold_collection.find_one({"_id": ObjectId(sold_id)})
        if not sold:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found")
        return SoldRecordResponse(**sold, id=str(sold["_id"]))

    async def update_sold_record(
        self,
        sold_id: str,
        update_data: SoldRecordCreate,
        token: str = Depends(get_current_user),
        get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
        sold_collection: Collection = Depends(get_sold_collection),
    ):
        # Similar update logic as the function version
        pass

    async def delete_sold_record(
        self,
        sold_id: str,
        token: str = Depends(get_current_user),
        get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
        sold_collection: Collection = Depends(get_sold_collection),
    ):
        # Similar delete logic as the function version
        pass

# Instantiate the controller and export its router
sold_stocks_controller = SoldStocksController()
router = sold_stocks_controller.router
