from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import get_sold_collection, get_current_stocks_collection
from models.model import SoldRecordCreate, SoldRecordResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

router = APIRouter()


@router.post("/sell_stocks")
async def create_sold_record(
    sold: SoldRecordCreate,
    token: str = Depends(get_current_user),
    get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
    get_sold_collection: Collection = Depends(get_sold_collection),
):
    purchase = get_current_stocks_collection.find_one(
        {"symbol": sold.symbol, "owner": token}
    )
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchase record found"
        )
    remaining_quantity = purchase["quantity"] - sold.quantity
    if remaining_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stocks to sell"
        )
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
    sold_data= sold.dict()
    sold_data["owner"]=token
    result= get_sold_collection.insert_one(sold_data)
    if not result:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to create sold record")
    return SoldRecordResponse(**sold_data, id= str(result.inserted_id))

@router.get("/sell_stocks", response_model=List[SoldRecordResponse])
async def get_sold_records(
    token: str = Depends(get_current_user),
    get_sold_collection: Collection = Depends(get_sold_collection),
):
    print(token)
    solds = get_sold_collection.find({"owner":token})
    if not solds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found"
        )
    return [SoldRecordResponse(**sold, id=str(sold["_id"])) for sold in solds]


@router.get("/sell_stocks/{sold_id}", response_model=SoldRecordResponse)
async def get_sold_record(
    sold_id: str,
    token: str = Depends(get_current_user),
    get_sold_collection: Collection = Depends(get_sold_collection),
):
    solds = get_sold_collection.find_one({"_id": ObjectId(sold_id)})
    if not solds:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found"
        )
    return SoldRecordResponse(**solds, id=str(solds["_id"]))


@router.put("/sell_stocks/{sold_id}", response_model=SoldRecordResponse)
async def update_sold_record(
    sold_id: str,
    update_data: SoldRecordCreate,
    token: str = Depends(get_current_user),
    get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
    sold_collection: Collection = Depends(get_sold_collection),
):

    existing_sold = sold_collection.find_one({"owner": token, "_id": ObjectId(sold_id)})
    if not existing_sold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found"
        )
    purchase = get_current_stocks_collection.find_one(
        {"symbol": update_data.symbol, "owner": token}
    )
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchase record found"
        )

    # revert the previous sold quantity and net profit
    reverted_quantity = purchase["quantity"] + existing_sold["quantity"]
    reverted_net_profit = purchase["net_profit"] - (
        existing_sold["price_per_unit_sold"] * existing_sold["quantity"]
    )
    remaining_quantity = reverted_quantity - update_data.quantity
    if remaining_quantity < 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Not enough stocks to sell"
        )

    # calculate the new net profit after applying the new sale
    update_net_profit = reverted_net_profit + (
        update_data.price_per_unit_sold * update_data.quantity
    )
    get_current_stocks_collection.update_one(
        {"_id": ObjectId(purchase["_id"])},
        {
            "$set": {
                "quantity": remaining_quantity,
                "net_profit": update_net_profit,
                "last_modified_at": datetime.now(),
            }
        },
    )
    # update the sold record with the new data
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["last_modified_at"] = datetime.utcnow()
    sold_collection.update_one({"_id": ObjectId(sold_id)}, {"$set": update_dict})
    updated_sold = sold_collection.find_one({"_id": ObjectId(sold_id)})
    return SoldRecordResponse(**updated_sold, id=str(updated_sold["_id"]))


@router.delete("/sell_stocks/{sold_id}", response_model=dict)
async def delete_sold_record(
    sold_id: str,
    token: str = Depends(get_current_user),
    get_current_stocks_collection: Collection = Depends(get_current_stocks_collection),
    sold_collection: Collection = Depends(get_sold_collection),
):

    existing_sold = sold_collection.find_one({"owner": token, "_id": ObjectId(sold_id)})
    if not existing_sold:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No sold record found"
        )
    purchase = get_current_stocks_collection.find_one(
        {"symbol": existing_sold["symbol"], "owner": token}
    )
    if not purchase:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No purchase record found"
        )

    # revert the previous sold quantity and net profit
    reverted_quantity = purchase["quantity"] + existing_sold["quantity"]
    reverted_net_profit = purchase["net_profit"] - (
        existing_sold["price_per_unit_sold"] * existing_sold["quantity"]
    )
    get_current_stocks_collection.update_one(
        {"_id": ObjectId(purchase["_id"])},
        {
            "$set": {
                "quantity": reverted_quantity,
                "net_profit": reverted_net_profit,
                "last_modified_at": datetime.now(),
            }
        },
    )

    result = sold_collection.delete_one({"_id": ObjectId(purchase["_id"])})
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete sold record",
        )
    return {"message": "Successfully deleted the sold record"}
