from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import get_current_user
from database.database import get_transaction_collection
from models.model import TransactionCreate, TransactionUpdate, TransactionResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

class TransactionRouter:
    def __init__(self):
        self.router = APIRouter()
        self.setup_routes()

    def setup_routes(self):
        self.router.add_api_route("/transactions", self.create_transaction, methods=["POST"], response_model=TransactionResponse)
        self.router.add_api_route("/transactions", self.get_transactions, methods=["GET"], response_model=List[TransactionResponse])
        self.router.add_api_route("/transactions/{transaction_id}", self.get_transaction, methods=["GET"], response_model=TransactionResponse)
        self.router.add_api_route("/transactions/{transaction_id}", self.update_transaction, methods=["PUT"], response_model=TransactionResponse)
        self.router.add_api_route("/transactions/{transaction_id}", self.delete_transaction, methods=["DELETE"], response_model=dict)

    async def create_transaction(self, transaction: TransactionCreate, 
                                  token: str = Depends(get_current_user), 
                                  db: Collection = Depends(get_transaction_collection)):
        transaction_data = transaction.dict()
        transaction_data["owner"] = token
        transaction_data["created_at"] = datetime.now()
        transaction_data["last_modified"] = datetime.now()
        result = db.insert_one(transaction_data)
        return TransactionResponse(**transaction_data, id=str(result.inserted_id))

    async def get_transactions(self, token: str = Depends(get_current_user), 
                                db: Collection = Depends(get_transaction_collection)):
        transactions = db.find({"owner": token})
        if transactions.count() == 0:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No transactions found")
        return [TransactionResponse(**t, id=str(t["_id"])) for t in transactions]

    async def get_transaction(self, transaction_id: str, 
                              token: str = Depends(get_current_user), 
                              db: Collection = Depends(get_transaction_collection)):
        transaction = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
        if not transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        return TransactionResponse(**transaction, id=str(transaction["_id"]))

    async def update_transaction(self, transaction_id: str, 
                                  update_data: TransactionUpdate, 
                                  token: str = Depends(get_current_user), 
                                  db: Collection = Depends(get_transaction_collection)):
        existing_transaction = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
        if not existing_transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        if existing_transaction.get("status_done"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction is already done")
        
        update_dict = update_data.dict(exclude_unset=True)
        update_dict["last_modified"] = datetime.utcnow()
        db.update_one({"_id": ObjectId(transaction_id)}, {"$set": update_dict})
        updated_transaction = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
        return TransactionResponse(**updated_transaction, id=str(updated_transaction["_id"]))

    async def delete_transaction(self, transaction_id: str, 
                                  token: str = Depends(get_current_user), 
                                  db: Collection = Depends(get_transaction_collection)):
        existing_transaction = db.find_one({"_id": ObjectId(transaction_id), "owner": token})
        if not existing_transaction:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Transaction not found")
        if existing_transaction.get("status_done"):
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Transaction is already done")
        
        db.delete_one({"_id": ObjectId(transaction_id)})
        return {"Message": "Transaction deleted successfully"}

# Instantiate and register the TransactionRouter
transaction_router_instance = TransactionRouter()
router = transaction_router_instance.router
