from routes.payment import payment
from routes.admin import admin
from routes.auth import auth
from config.db_config import engine, Base
from routes.users import user
from routes.products import product
from routes.cart import cart
from routes.category import category
from routes.orders import orders
from dotenv import load_dotenv
from os.path import join, dirname
from helper.api_helper import APIHelper
from helper.cors_helper import CORSHelper
from helper.logger_helper import setup_logger
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
import i18n




# Setting up dotenv
dotenv_path = join(dirname(__file__), "..", ".env")
load_dotenv(dotenv_path)
# Importing libraries

#Setup Logger
# setup_logger()

# Setup i18n
i18n.load_path.append('language/')
i18n.set("filename_format", "{namespace}.{locale}.{format}")
i18n.set("file_format", "json")

# Initializing app
app = FastAPI(
    title="Boilerplate-FastAPI",
    version="0.0.1",
)

#Setup CORS
CORSHelper.setup_cors(app)

# Request validation error
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    if exc.errors()[0]['type'] == 'value_error':
        return APIHelper.send_error_response(
            errorMessageKey =f"{exc.errors()[0]['msg']}"
        )
    else:
        return APIHelper.send_error_response(
            errorMessageKey =f"{exc.errors()[0]['loc'][1]} {exc.errors()[0]['msg']}")

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    errors = exc.errors()
    # Pydantic errors usually come in a list; we grab the first one
    first_error = errors[0]
    location = first_error['loc']
    
    # location is a tuple like ('body', 'email') or ('query', 'product_id')
    # If the whole body is missing, len(location) might be 1
    field_name = location[1] if len(location) > 1 else location[0]
    message = first_error['msg']
    
    # This uses your APIHelper to send a standard 400 error
    return APIHelper.send_error_response(
        errorMessageKey=f"{field_name} {message}"
    )

Base.metadata.create_all(bind=engine)

app.include_router(auth)
app.include_router(user)
app.include_router(admin)
app.include_router(product)
app.include_router(cart)
app.include_router(category)
app.include_router(orders)
app.include_router(payment)