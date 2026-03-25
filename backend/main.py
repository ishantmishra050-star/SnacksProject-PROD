import os
import html
from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .api import auth, stores, products, orders, users

# Create all tables
Base.metadata.create_all(bind=engine)

# ─── Environment config ───
ENV = os.getenv("APP_ENV", "development")
IS_PROD = ENV == "production"

app = FastAPI(
    title="Vintage Indian Snacks API",
    description="E-commerce API connecting offline vintage snack shops with customers worldwide",
    version="1.0.0",
    # Disable Swagger UI in production
    docs_url=None if IS_PROD else "/docs",
    redoc_url=None if IS_PROD else "/redoc",
    openapi_url=None if IS_PROD else "/openapi.json",
)

# ─── CORS — restrict origins via env var ───
ALLOWED_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "https://snack-projectv10.vercel.app,https://snacks-project-mfmx.vercel.app,http://localhost:5173,http://localhost:5174,http://localhost:3000"
).split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)


# ─── Security Headers Middleware ───
@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-XSS-Protection"] = "1; mode=block"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Permissions-Policy"] = "camera=(), microphone=(), geolocation=()"
    if IS_PROD:
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
    return response


# Include routers
app.include_router(auth.router)
app.include_router(stores.router)
app.include_router(products.router)
app.include_router(orders.router)
app.include_router(users.router)


@app.get("/")
def root():
    return {
        "name": "Vintage Indian Snacks API",
        "version": "1.0.0",
    }
