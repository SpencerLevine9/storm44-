from fastapi import APIRouter
from app.schemas.ask import AskRequest, AskResponse

router = APIRouter()


@router.post("/ask", response_model=AskResponse)
def ask(req: AskRequest) -> AskResponse:

    # Deterministic stub: echoes the query. Later replaced by RagEngine.
    
    return AskResponse(
        answer=f"(stub) You asked: {req.query}",
        citations=[],
    )