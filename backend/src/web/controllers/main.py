import time

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import PlainTextResponse
from starlette.middleware.sessions import SessionMiddleware

from src.auth.config import SECRET_KEY

from .about import router as about_router
from .api.action import router as action_api_router
from .api.areas import router as areas_api_router
from .api.config import router as config_router
from .api.reactions import router as reactions_api_router
from .api.service import router as service_api_router
from .api.triggers import router as triggers_api_router
from .api.user_services import router as user_services_router
from .auth import router as auth_router
from .oauth import router as oauth_router

app = FastAPI()

# Middleware to allow CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://137.74.94.58:8081", "http://localhost:8081"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY,
)

# Include routers
app.include_router(auth_router)
app.include_router(oauth_router)
app.include_router(about_router)
app.include_router(service_api_router)
app.include_router(reactions_api_router)
app.include_router(triggers_api_router)
app.include_router(service_api_router)
app.include_router(action_api_router)
app.include_router(areas_api_router)
app.include_router(user_services_router)
app.include_router(config_router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Your API Title",
        version="1.0.0",
        description="Your API Description",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/session-test")
async def session_test(request: Request):
    request.session["test_key"] = "test_value"
    return {"message": "Session set!"}


@app.get("/session-fetch")
async def session_fetch(request: Request):
    return {"session_value": request.session.get("test_key")}


@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    print(f"Request headers: {request.headers}")  # Debugging
    response = await call_next(request)
    process_time = time.time() - start_time
    print(
        f"Request: {request.method} {request.url} completed in {process_time:.4f} seconds"
    )
    return response


@app.get("/", response_class=PlainTextResponse)
def read_root() -> str:
    return "Hello World"
