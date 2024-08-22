from fastapi import FastAPI

from routes.notes import router as notes_router
from routes.expense import router as expense_router
from routes.transaction import router as transaction_router
from routes.user import router as user_router
from routes.user_stocks import router as user_stocks_router
from routes.stock_historical_data import router as stock_historical_data
from routes.buy_stocks import router as buy_stocks_router
from routes.sold_stocks import router as sold_stocks_router
app = FastAPI()

app.include_router(user_router, prefix="/api",tags=["User Details"])
app.include_router(notes_router, prefix="/api",tags=["Notes"])
app.include_router(expense_router, prefix="/api",tags=["Expenses"])
app.include_router(transaction_router, prefix="/api",tags=["Transactions"])
app.include_router(user_stocks_router, prefix="/api",tags=["User Stock"])
app.include_router(stock_historical_data, prefix="/api",tags=["Historical Stock Data"])
app.include_router(buy_stocks_router, prefix="/api",tags=["Buy Stock"])
app.include_router(sold_stocks_router, prefix="/api",tags=["Sell Stock"])