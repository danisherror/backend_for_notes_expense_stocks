from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import get_purchase_collection, get_current_stocks_collection
from models.model import PurchaseRecordCreate, PurchaseRecordResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

router = APIRouter()


@router.post("/but_stocks", response_model=PurchaseRecordResponse)
async def create_purchase_record(
    purchase: PurchaseRecordCreate,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_purchase_collection),
    current_stocks_db: Collection = Depends(get_current_stocks_collection),
):
    purchase_dict = purchase.dict()
    purchase_dict["created_at"] = datetime.now()
    purchase_dict["owner"] = token
    purchase_dict["last_modified"] = datetime.now()
    result = db.insert_one(purchase_dict)
    prev_data = current_stocks_db.find_one(
        {"owner": token, "symbol": purchase_dict["symbol"]}
    )
    net_profit = float(purchase_dict["price_per_unit"]) * float(
        purchase_dict["quantity"]
    )
    net_profit = net_profit * (-1)
    if not prev_data:
        current_stocks_db.insert_one(
            {
                "owner": token,
                "name": purchase_dict["name"],
                "symbol": purchase_dict["symbol"],
                "price_per_unit": purchase_dict["price_per_unit"],
                "quantity": purchase_dict["quantity"],
                "created_at": purchase_dict["created_at"],
                "last_updated": datetime.now(),
                "net_profit": net_profit,
            }
        )
    else:
        prev_net_profit = prev_data["net_profit"] + net_profit
        average_price_per_unit = float(
            float(prev_data["price_per_unit"]) * float(prev_data["quantity"])
            + float(purchase_dict["quantity"]) * float(purchase_dict["price_per_unit"])
        )
        total_quantity = prev_data["quantity"] + purchase_dict["quantity"]
        average_price_per_unit = float(average_price_per_unit / total_quantity)
        current_stocks_db.update_one(
            {"_id": prev_data["_id"]},
            {
                "$set": {
                    "quantity": total_quantity,
                    "net_profit": prev_net_profit,
                    "last_updated": datetime.now(),
                    "price_per_unit": average_price_per_unit,
                }
            },
        )
    return PurchaseRecordResponse(**purchase_dict, id=str(result.inserted_id))


@router.get("/buy_stocks", response_model=List[PurchaseRecordResponse])
async def get_purchases(
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_purchase_collection),
):
    purchases = db.find({"owner": token})
    if not purchases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found"
        )
    return [
        PurchaseRecordResponse(**purchase, id=str(purchase["_id"]))
        for purchase in purchases
    ]


@router.get("/buy_stocks/{purchase_id}", response_model=PurchaseRecordResponse)
async def get_purchase(
    purchase_id: str,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_purchase_collection),
):
    purchases = db.find_one({"owner": token, "_id": ObjectId(purchase_id)})
    if not purchases:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found"
        )
    return PurchaseRecordResponse(**purchases, id=str(purchases["_id"]))


@router.put("/buy_stocks/{purchase_id}", response_model=PurchaseRecordResponse)
async def update_buy_record(
    purchase_id: str,
    updated_data: PurchaseRecordCreate,
    token: str = Depends(get_current_user),
    purchases_collection: Collection = Depends(get_purchase_collection),
    current_stock_collection: Collection = Depends(get_current_stocks_collection),
):
    existing_purchase = purchases_collection.find_one(
        {"_id": ObjectId(purchase_id), "owner": token}
    )
    if not existing_purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found"
        )
    prev_data = current_stock_collection.find_one(
        {"owner": token, "symbol": existing_purchase["symbol"]}
    )
    # first revert the average price
    prev_price_per_unit = (
        prev_data["price_per_unit"] * prev_data["quantity"]
        - existing_purchase["price_per_unit"] * existing_purchase["quantity"]
    )
    reverted_quantity = prev_data["quantity"] - existing_purchase["quantity"]
    if reverted_quantity == 0:
        average_price_per_unit = 0
    else:
        average_price_per_unit = float(prev_price_per_unit / reverted_quantity)
    reverted_net_profit = prev_data["net_profit"] + (
        existing_purchase["price_per_unit"] * existing_purchase["quantity"]
    )
    updated_net_profit = reverted_net_profit - (
        updated_data.price_per_unit * updated_data.quantity
    )
    remaining_quantity = reverted_quantity + updated_data.quantity
    average_price_per_unit = float(
        average_price_per_unit * reverted_quantity
        + float(updated_data.price_per_unit * updated_data.quantity)
    )
    total_quantity = reverted_quantity + updated_data.quantity
    average_price_per_unit = float(average_price_per_unit / total_quantity)
    current_stock_collection.update_one(
        {"_id": ObjectId(prev_data["_id"])},
        {
            "$set": {
                "symbol": updated_data.symbol,
                "name": updated_data.name,
                "quantity": remaining_quantity,
                "net_profit": updated_net_profit,
                "last_modified_at": datetime.now(),
                "price_per_unit": average_price_per_unit,
            }
        },
    )
    updated_dict = updated_data.dict(exclude_unset=True)
    updated_dict["last_modified_at"] = datetime.utcnow()
    purchases_collection.update_one(
        {"_id": ObjectId(purchase_id)}, {"$set": updated_dict}
    )
    updated_purchase = purchases_collection.find_one({"_id": ObjectId(purchase_id)})
    if not updated_purchase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to update purchase record",
        )
    return PurchaseRecordResponse(**updated_purchase, id=str(updated_purchase["_id"]))


@router.delete("/buy_stocks/{purchase_id}", response_model=dict)
async def delete_buy_record(
    purchase_id: str,
    token: str = Depends(get_current_user),
    purchases_collection: Collection = Depends(get_purchase_collection),
    current_stock_collection: Collection = Depends(get_current_stocks_collection),
):
    existing_purchase = purchases_collection.find_one(
        {"_id": ObjectId(purchase_id), "owner": token}
    )
    if not existing_purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchases found"
        )
    prev_data = current_stock_collection.find_one(
        {"owner": token, "symbol": existing_purchase["symbol"]}
    )
    # first revert the average price
    prev_price_per_unit = (
        prev_data["price_per_unit"] * prev_data["quantity"]
        - existing_purchase["price_per_unit"] * existing_purchase["quantity"]
    )
    reverted_quantity = prev_data["quantity"] - existing_purchase["quantity"]
    if reverted_quantity == 0:
        average_price_per_unit = 0
    else:
        average_price_per_unit = float(prev_price_per_unit / reverted_quantity)
    reverted_net_profit = prev_data["net_profit"] + (
        existing_purchase["price_per_unit"] * existing_purchase["quantity"]
    )
    current_stock_collection.update_one(
        {"_id": ObjectId(prev_data["_id"])},
        {
            "$set": {
                "quantity": reverted_quantity,
                "net_profit": reverted_net_profit,
                "last_modified_at": datetime.now(),
                "price_per_unit": average_price_per_unit,
            }
        },
    )
    updated_purchase = purchases_collection.delete_one({"_id": ObjectId(purchase_id)})
    if not updated_purchase:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unable to delete purchase record",
        )
    return {"message": "Purchase was successfully deleted"}
