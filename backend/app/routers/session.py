from fastapi import APIRouter
from app.models.request_models import CreateSessionRequest
from app.models.response_models import SessionResponse
from app.services import session_service

router = APIRouter(prefix="/sessions", tags=["sessions"])


@router.post("", response_model=SessionResponse)
def create_session(body: CreateSessionRequest):
    sid = session_service.create_session(body.datasource_id)
    return SessionResponse(session_id=sid)


@router.delete("/{session_id}")
def delete_session(session_id: str):
    session_service.delete_session(session_id)
    return {"status": "deleted"}
