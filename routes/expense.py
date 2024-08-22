from fastapi import APIRouter, HTTPException, Depends, status
from typing import List
from auth.auth import decode_jwt_token, get_current_user
from database.database import get_expense_collection
from models.model import ExpenseCreate, ExpenseUpdate, ExpenseResponse
from bson import ObjectId
from datetime import datetime
from pymongo.collection import Collection

router = APIRouter()


@router.post("/expenses", response_model=ExpenseResponse)
async def create_expense(
    expense: ExpenseCreate,
    token: str = Depends(get_current_user),
    expense_collection: Collection = Depends(get_expense_collection),
):
    expense_data = expense.dict()
    expense_data["owner"] = token
    expense_data["created_at"] = datetime.now()
    expense_data["last_modified"] = datetime.now()
    result = expense_collection.insert_one(expense_data)
    return ExpenseResponse(**expense_data, id=str(result.inserted_id))


@router.get("/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    token: str = Depends(get_current_user),
    expense_collection: Collection = Depends(get_expense_collection),
):
    expenses = expense_collection.find({"owner": token})
    if not expenses:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="No expenses found"
        )
    return [ExpenseResponse(**expense, id=str(expenses["_id"])) for expense in expenses]


@router.get("/expenses/{expenses_id}", response_model=ExpenseResponse)
async def get_expense(
    expenses_id: str,
    token: str = Depends(get_current_user),
    expense_collection: Collection = Depends(get_expense_collection),
):
    expense = expense_collection.find_one(
        {"_id": ObjectId(expenses_id), "owner": token}
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )
    return ExpenseResponse(**expense, id=str(expense["_id"]))


@router.delete("/expenses/{expenses_id}", response_model=dict)
async def delete_expenses(
    expenses_id: str,
    token: str = Depends(get_current_user),
    expense_collection: Collection = Depends(get_expense_collection),
):
    expense = expense_collection.find_one(
        {"_id": ObjectId(expenses_id), "owner": token}
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    if expense.get("status_done"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Expense is already done"
        )
    expense_collection.delete_one({"_id": ObjectId(expenses_id)})
    return {"Message": "Expense deleted successfully"}


@router.put("/expenses/{expenses_id}", response_model=ExpenseResponse)
async def update_expenses(
    expenses_id: str,
    update_data: ExpenseUpdate,
    token: str = Depends(get_current_user),
    expense_collection: Collection = Depends(get_expense_collection),
):
    expense = expense_collection.find_one(
        {"_id": ObjectId(expenses_id), "owner": token}
    )

    if not expense:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Expense not found"
        )

    if expense.get("status_done"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Expense is already done"
        )
    update_dict = update_data.dict(exclude_unset=True)
    update_dict["last_modified"] = datetime.utcnow()
    expense_collection.update_one({"_id": ObjectId(expenses_id)}, {"$set": update_dict})
    update_expenses = expense_collection.find_one({"_id": ObjectId(expenses_id)})
    return ExpenseResponse(**update_expenses, id=str(update_expenses["_id"]))
