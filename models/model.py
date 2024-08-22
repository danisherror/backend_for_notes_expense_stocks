from pydantic import BaseModel, EmailStr, validator
from typing import List, Optional
from datetime import datetime

################################################################
#                   User Basic                                 #
################################################################


class User(BaseModel):
    email: EmailStr
    password: str


class UserInDB(User):
    hashed_password: str


class UserOut(BaseModel):
    email: EmailStr
    id: str


################################################################
#                   Notes                                      #
################################################################
class NoteBase(BaseModel):
    title: str
    content: str
    tags: List[str] = []
    folder: str = "Untitled"
    status: str = "in development"
    priority: str = "medium"
    created_at: datetime
    last_modified: datetime


class NoteCreate(NoteBase):
    pass


class NoteUpdate(NoteBase):
    title: Optional[str]
    content: Optional[str]
    tags: Optional[List[str]]
    folder: Optional[str]
    status: Optional[str]
    priority: Optional[str]


class NoteInDB(NoteBase):
    id: str


class NoteResponse(NoteInDB):
    owner: str


################################################################
#                   Expense                                    #
################################################################


class ExpenseBase(BaseModel):
    amount: float
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    split_amount: Optional[List[str]] = None
    amount_given: Optional[bool] = False
    status_done: Optional[bool] = False



class ExpenseCreate(ExpenseBase):
    pass


class ExpenseUpdate(BaseModel):
    amount: float
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    split_amount: Optional[List[str]] = None
    amount_given: Optional[bool] = False
    status_done: Optional[bool] = False

    class Config:
        extra = "forbid"


class ExpenseResponse(ExpenseBase):
    id: str
    created_at: datetime
    last_modified: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


################################################################
#                   Transaction                                #
################################################################


class TransactionBase(BaseModel):
    amount: float
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    transaction_type: Optional[str] = None  # income or expense
    transaction_date: Optional[datetime] = None  # transaction
    status_done: Optional[bool] = False
    second_party: Optional[str] = None


class TransactionCreate(TransactionBase):
    pass


class TransactionUpdate(BaseModel):
    amount: float
    description: Optional[str] = None
    tags: Optional[List[str]] = []
    transaction_type: Optional[str] = None  # income or expense
    transaction_date: Optional[datetime] = None  # transaction
    status_done: Optional[bool] = False
    second_party: Optional[str] = None

    class Config:
        extra = "forbid"


class TransactionResponse(TransactionBase):
    id: str
    created_at: datetime
    last_modified: datetime

    class Config:
        orm_mode = True
        allow_population_by_field_name = True


################################################################
#                   Stock Current                              #
################################################################


class CurrentStockRecordCreate(BaseModel):
    symbol: str
    name: Optional[str] = None
    price_per_unit: float
    quantity: int
    created_at: datetime
    last_updated: datetime
    net_profit: Optional[float] = None


class CurrentStockRecordResponse(BaseModel):
    symbol: str
    name: Optional[str] = None
    price_per_unit: float
    quantity: int
    created_at: datetime
    last_updated: datetime
    net_profit: Optional[float] = None
    owner: str

    class Config:
        orm_mode = True


################################################################
#                   Stocks purchased                           #
################################################################

class PurchaseRecordCreate(BaseModel):
    symbol: str
    name: Optional[str] = None
    timestamp: datetime
    price_per_unit: float
    quantity: int
    created_at: datetime
    last_updated: datetime
    
class PurchaseRecordResponse(BaseModel):
    symbol: str
    id: str
    name: Optional[str] = None
    timestamp: datetime
    price_per_unit: float
    quantity: int
    created_at: datetime
    last_updated: datetime
    
    class Config:
        orm_mode = True
        

################################################################
#                   Stocks purchased                           #
################################################################


class SoldRecordCreate(BaseModel):
    symbol: str
    timestamp: datetime
    price_per_unit_sold: float
    quantity: int
    created_at: datetime
    last_updated: datetime
    
class SoldRecordResponse(BaseModel):
    id: str
    symbol: str
    timestamp: datetime
    price_per_unit_sold: float
    quantity: int
    created_at: datetime
    last_updated: datetime

    class Config:
        orm_mode = True



################################################################
#                   Stocks purchased                           #
################################################################


class StockHistory(BaseModel):
    symbol: str
    name: Optional[str]=None
    history: list[dict] # historical record of stock
    history_last_month: list[dict] # historical record of last minth
    history_last_week: list[dict] # historical record of last week
    history_last_one_day: list[dict] # historical record of last day
    created_at: datetime
    last_modified_at: datetime
class StockResponse(BaseModel):
    id: str
    symbol: str
    name: Optional[str]=None
    history: list[dict] # historical record of stock
    history_last_month: list[dict] # historical record of last minth
    history_last_week: list[dict] # historical record of last week
    history_last_one_day: list[dict] # historical record of last day
    created_at: datetime
    last_modified_at: datetime
    class Config:
        orm_mode = True