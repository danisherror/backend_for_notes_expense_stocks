from fastapi import FastAPI
import time
import logging
import logging.config
from typing import Union
import uvicorn
from uvicorn.config import LOGGING_CONFIG
from fastapi.middleware.cors import CORSMiddleware
from routes.notes import router as notes_router
from routes.expense import router as expense_router
from routes.transaction import router as transaction_router
from routes.user import router as user_router
from routes.user_stocks import router as user_stocks_router
from routes.stock_historical_data import router as stock_historical_data
from routes.buy_stocks import router as buy_stocks_router
from routes.sold_stocks import router as sold_stocks_router
app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Allow specific origins
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
)

app.include_router(user_router, prefix="/api",tags=["User Details"])
app.include_router(notes_router, prefix="/api",tags=["Notes"])
app.include_router(expense_router, prefix="/api",tags=["Expenses"])
app.include_router(transaction_router, prefix="/api",tags=["Transactions"])
app.include_router(user_stocks_router, prefix="/api",tags=["User Stock"])
app.include_router(stock_historical_data, prefix="/api",tags=["Historical Stock Data"])
app.include_router(buy_stocks_router, prefix="/api",tags=["Buy Stock"])
app.include_router(sold_stocks_router, prefix="/api",tags=["Sell Stock"])

def set_logging(log_file):
    # Formatter commun
    file_format = "%(asctime)s %(levelname)-8s : %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    formatter = logging.Formatter(file_format, datefmt=date_format)

    # Setup File Handler
    file_handler = logging.FileHandler(log_file, encoding="utf-8")
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)

    # Setup Console Handler (affiche dans la console)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    # Configure logging pour Uvicorn
    LOGGING_CONFIG["formatters"]["access"]["fmt"] = file_format
    LOGGING_CONFIG["formatters"]["default"]["fmt"] = file_format
    LOGGING_CONFIG["formatters"]["default"]["datefmt"] = date_format
    LOGGING_CONFIG["formatters"]["access"]["datefmt"] = date_format

    # Définition des handlers pour les logs dans Uvicorn
    LOGGING_CONFIG["handlers"]["default"] = {
        "class": "logging.FileHandler",
        "formatter": "default",
        "level": "INFO",
        "filename": log_file
    }

    LOGGING_CONFIG["handlers"]["access"] = {
        "class": "logging.FileHandler",
        "formatter": "access",
        "level": "INFO",
        "filename": log_file
    }

    # Ajouter le console handler à la configuration par défaut
    LOGGING_CONFIG["handlers"]["console"] = {
        "class": "logging.StreamHandler",
        "formatter": "default",
        "level": "INFO"
    }

    LOGGING_CONFIG["loggers"]["uvicorn"]["handlers"] = ["default", "console"]
    LOGGING_CONFIG["loggers"]["uvicorn.access"]["handlers"] = ["access", "console"]

    # Appliquer la configuration de logging
    logging.config.dictConfig(LOGGING_CONFIG)

def main():
    log_file = f"log_{time.strftime('%Y_%m_%d_%H_%M_%S')}.log"
    set_logging(log_file)

    uvicorn.run("main:app", host="0.0.0.0",
                port=8000,
                log_level="info",
                proxy_headers=True,
                root_path="",
                use_colors=False)
if __name__ == "__main__":
    main()