from fastapi import APIRouter
from pydantic import BaseModel
from ..services import ai_service


class SearchRequest(BaseModel):
    query: str


router = APIRouter(
    prefix="/ai",
    tags=["ai"]
)

@router.post("/search")
async def search_ai(search_request: SearchRequest):
    return ai_service.search_ai(search_request.query)