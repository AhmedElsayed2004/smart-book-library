from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from .auth import get_current_user, SECRET_KEY, ALGORITHM
from ..database import SessionLocal
from sqlalchemy.orm import Session

from ..models import ChatSession, ChatMessage, Book
from ..services import ai_service
from jose import jwt, JWTError
import json


class SessionCreateRequest(BaseModel):
    book_id: int


class QuestionRequest(BaseModel):
    question: str


router = APIRouter(
    prefix="/sessions",
    tags=["sessions"]
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependency = Annotated[dict, Depends(get_current_user)]


def check_user_session_permission(use_id: int, session_id: int, db):
    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()

    if not session:
        return None

    return session.user_id == use_id


@router.get("")
async def get_all_sessions(db: db_dependency, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")
    result = db.query(ChatSession).filter(ChatSession.user_id == user.get('id')).all()
    return result


@router.get("/{session_id}")
async def get_session_messages(db: db_dependency, session_id: int, user: user_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    # ensure that this session belong to that user
    permission = check_user_session_permission(user.get("id"), session_id, db)
    if permission is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not permission:
        raise HTTPException(status_code=403, detail="Not allowed to access this session")

    result = db.query(ChatMessage).filter(ChatMessage.session_id == session_id).all()
    return result


#
# @router.websocket("/{session_id}/chat/")
# async def websocket_ai_chat(
#         websocket: WebSocket,
#         db: db_dependency,
#         token: str,
#         session_id: int):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         user_id = payload.get("id")
#         if user_id is None:
#             raise HTTPException(status_code=401, detail="Invalid token")
#     except JWTError:
#         await websocket.close(code=1008)
#         return
#
#     permission = check_user_session_permission(user_id, session_id, db)
#     if permission is None:
#         raise HTTPException(status_code=404, detail="Session not found")
#     if not permission:
#         raise HTTPException(status_code=403, detail="Not allowed to access this session")
#
#     session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
#     book = db.query(Book).filter(Book.id == session.book_id).first()
#
#     await websocket.accept()
#
#     try:
#         while True:
#             question = await websocket.receive_text()
#
#             answer = await ai_service.answer_about_book(question, book.slug)
#
#             question_model = ChatMessage(session_id=session_id, sender='user', content=question)
#             answer_model = ChatMessage(session_id=session_id, sender='AI', content=answer)
#
#             db.add(question_model)
#             db.add(answer_model)
#             db.commit()
#
#             # send back the answer (you can also stream in chunks here)
#             await websocket.send_text(answer)
#
#     except WebSocketDisconnect:
#         print(f"Client disconnected from session {session_id}")
@router.post("/{session_id}/chat")
async def ask_ai_about_book(db: db_dependency, session_id: int, user: user_dependency,
                            question_request: QuestionRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    permission = check_user_session_permission(user.get('id'), session_id, db)
    if permission is None:
        raise HTTPException(status_code=404, detail="Session not found")
    if not permission:
        raise HTTPException(status_code=403, detail="Not allowed to access this session")

    session = db.query(ChatSession).filter(ChatSession.id == session_id).first()
    book = db.query(Book).filter(Book.id == session.book_id).first()

    async def event_publisher():
        async for chunk in ai_service.answer_about_book(question_request.question, book.slug):
            payload = {"data": chunk}
            yield f"data: {json.dumps(payload)}\n\n"
        yield "data: [DONE]\n\n"

    return StreamingResponse(event_publisher(), media_type="text/event-stream")


@router.post("")
async def create_new_session(db: db_dependency, user: user_dependency, session_create_request: SessionCreateRequest):
    if user is None:
        raise HTTPException(status_code=401, detail="Authentication Failed")

    book = db.query(Book).filter(Book.id == session_create_request.book_id).first()

    if book is None:
        raise HTTPException(status_code=404, detail="Book not found")

    session = ChatSession(user_id=user.get('id'), book_id=session_create_request.book_id)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session
