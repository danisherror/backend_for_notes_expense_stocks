from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import  get_current_user
from database.database import get_transaction_collection
from models.model import TransactionCreate, TransactionUpdate, TransactionResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

router = APIRouter()


@router.post("/transactions", response_model=TransactionResponse)
async def create_transaction(
    transaction: TransactionCreate,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_transaction_collection),
):
    transaction_data = transaction.dict()
    transaction_data["owner"] = token
    transaction_data["created_at"] = datetime.now()
    transaction_data["last_modified"] = datetime.now()
    result = db.insert_one(transaction_data)
    return TransactionResponse(**transaction_data, id=str(result.inserted_id))


@router.get("/transactions", response_model=List[TransactionResponse])
async def get_transactions(
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_transaction_collection),
):
    transactions = db.find({"owner": token})
    if not transactions:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No transactions found"
        )
    return [TransactionResponse(**t, id=str(t["_id"])) for t in transactions]


@router.get("/transactions/{transaction_id}", response_model=TransactionResponse)
async def get_transaction(
    transaction_id: str,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_transaction_collection),
):
    transaction = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
    if not transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    return TransactionResponse(**transaction, id=str(transaction["_id"]))


@router.put("/transactions/{transaction_id}", response_model=TransactionResponse)
async def update_transaction(
    transaction_id: str,
    update_data: TransactionUpdate,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_transaction_collection),
):
    existing_transaction = db.find_one(
        {"_id": ObjectId(transaction_id), "owner": token}
    )
    if not existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    if existing_transaction.get("status_done"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already done",
        )
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["last_modified"] = datetime.utcnow()
    db.update_one({"_id": ObjectId(transaction_id)}, {"$set": update_dict})
    update_transactions = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
    return TransactionResponse(
        **update_transactions, id=str(update_transactions["_id"])
    )


@router.delete("/transactions/{transaction_id}", response_model=dict)
async def delete_transaction(
    transaction_id: str,
    token: str = Depends(get_current_user),
    db: Collection = Depends(get_transaction_collection),
):
    existing_transaction = db.find_one(
        {"_id": ObjectId(transaction_id), "owner": token}
    )
    if not existing_transaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found"
        )
    if existing_transaction.get("status_done"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Transaction is already done",
        )
    db.delete_one({"_id": ObjectId(transaction_id)})
    return {"Message": "Transaction deleted successfully"}
