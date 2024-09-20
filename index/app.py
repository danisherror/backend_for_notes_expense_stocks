import time
import logging
import logging.config
from typing import Union
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response
from uvicorn.config import LOGGING_CONFIG
from routes.notes import router as notes_router
from routes.expense import router as expense_router
from routes.transaction import router as transaction_router
from routes.user import router as user_router
from routes.user_stocks import router as user_stocks_router
from routes.stock_historical_data import router as stock_historical_data
from routes.buy_stocks import router as buy_stocks_router
from routes.sold_stocks import router as sold_stocks_router
class MyApp:
    def __init__(self):
        self.app = FastAPI()
        self.setup_logging()
        self.setup_middleware()
        self.setup_routes()
        self.app.middleware("http")(self.log_requests)

    def setup_logging(self):
        
        log_file = f"log_{time.strftime('%Y_%m_%d_%H_%M_%S')}.log"
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
        self.log = logging.getLogger("uvicorn")
    def setup_middleware(self):
        # Adding CORS Middleware
        self.app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:5173"],  # Allow specific origins
            allow_credentials=True,
            allow_methods=["*"],  # Allow all HTTP methods
            allow_headers=["*"],  # Allow all headers
        )
    def setup_routes(self):
        self.app.include_router(user_router, prefix="/api",tags=["User Details"])
        self.app.include_router(notes_router, prefix="/api",tags=["Notes"])
        self.app.include_router(expense_router, prefix="/api",tags=["Expenses"])
        self.app.include_router(transaction_router, prefix="/api",tags=["Transactions"])
        self.app.include_router(user_stocks_router, prefix="/api",tags=["User Stock"])
        self.app.include_router(stock_historical_data, prefix="/api",tags=["Historical Stock Data"])
        self.app.include_router(buy_stocks_router, prefix="/api",tags=["Buy Stock"])
        self.app.include_router(sold_stocks_router, prefix="/api",tags=["Sell Stock"])


    async def log_requests(self, request: Request, call_next):
        response: Response = await call_next(request)
        try:
            status_code = str(response.status_code)
            message = f"Request {request.method} {request.url} called with {response.status_code} status"
            if status_code[0] == "2":
                self.log.info(message)
            elif status_code[0] == "3":
                self.log.warning(message)
            elif status_code[0] == "4":
                self.log.error(message)
            elif status_code[0] == "5":
                self.log.critical(message)
            else:
                self.log.debug(message)
        except Exception as e:
            self.log.error(f"Error while logging request: {str(e)}")
        return response

app_inst = MyApp()
app = app_inst.app