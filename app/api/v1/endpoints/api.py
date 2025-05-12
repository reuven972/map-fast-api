from fastapi import APIRouter
from app.api.v1.endpoints.argument_map import router as argument_map_router

# Central router for version 1 of the API
router_v1 = APIRouter()

# Include the argument_map router with a prefix and tags
router_v1.include_router(
    argument_map_router,
    prefix="/argument_map",
    tags=["argument_map"]
)