from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.core.logging import setup_logging
from app.api.v1.endpoints import argument_map
from app.api.v1.endpoints.api import router_v1  # Import the central router


# Initialize FastAPI app
app = FastAPI(title=settings.APP_NAME, version=settings.APP_VERSION)

# Setup logging
setup_logging()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,  # List[str] from settings
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the v1 API routes
app.include_router(router_v1, prefix="/api/v1")

@app.get("/")
async def root():
    return {"message": "Welcome to the Argument Map API"}