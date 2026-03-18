"""
Asklytics: Conversation history API endpoints.
Provides GET conversations list, GET single conversation, POST new conversation.
"""
import logging
from uuid import UUID
from fastapi import APIRouter, HTTPException, Depends, Header
from app.models.auth_models import Conversation, ConversationListItem, ConversationCreateRequest, ConversationTurnCreate
from app.services.auth_service import AuthService
from app.services.supabase_service import (
    list_conversations,
    get_conversation,
    create_conversation,
    add_conversation_turn,
    delete_conversation
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/conversations", tags=["conversations"])


async def get_current_user_id(authorization: str = Header(None)) -> str:
    """Extract user_id from JWT token."""
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing authorization header")

    token = AuthService.extract_token_from_header(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Invalid authorization header")

    user_id = AuthService.verify_access_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="Invalid or expired access token")

    return user_id


@router.get("/", response_model=list)
async def list_user_conversations(
    user_id: str = Depends(get_current_user_id),
    limit: int = 50,
    offset: int = 0
):
    """List all conversations for the authenticated user."""
    try:
        conversations = await list_conversations(user_id, limit, offset)
        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise HTTPException(status_code=500, detail="Failed to load conversations")


@router.get("/{conversation_id}")
async def get_single_conversation(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user_id)
):
    """Get a single conversation with all its turns."""
    try:
        conversation = await get_conversation(str(conversation_id))

        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")

        # Verify user owns this conversation (RLS should handle this, but double-check)
        if conversation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        return conversation
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to load conversation")


@router.post("/", response_model=dict)
async def create_new_conversation(
    request: ConversationCreateRequest,
    user_id: str = Depends(get_current_user_id)
):
    """Create a new conversation."""
    try:
        conversation = await create_conversation(user_id, request.title, request.datasource_id)
        return {
            "id": str(conversation["id"]),
            "created_at": conversation["created_at"],
            "message": "Conversation created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to create conversation")


@router.delete("/{conversation_id}")
async def delete_conversation_endpoint(
    conversation_id: UUID,
    user_id: str = Depends(get_current_user_id)
):
    """Delete a conversation (cascades to all turns)."""
    try:
        # Verify ownership first
        conversation = await get_conversation(str(conversation_id))
        if not conversation or conversation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        await delete_conversation(str(conversation_id))
        return {"message": "Conversation deleted successfully"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise HTTPException(status_code=500, detail="Failed to delete conversation")


@router.post("/{conversation_id}/turns")
async def add_turn_to_conversation(
    conversation_id: UUID,
    request: ConversationTurnCreate,
    user_id: str = Depends(get_current_user_id)
):
    """Add a turn (question and answer pair) to a conversation."""
    try:
        # Verify ownership first
        conversation = await get_conversation(str(conversation_id))
        if not conversation or conversation.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized access")

        turn = await add_conversation_turn(
            conversation_id=str(conversation_id),
            user_prompt=request.user_prompt,
            sql_generated=request.sql_generated,
            charts=request.charts,
            insight_summary=request.insight_summary,
            data_limitations=request.data_limitations,
            execution_time_ms=request.execution_time_ms
        )
        return {"message": "Turn added successfully", "turn_id": str(turn.get("id", ""))}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding turn: {e}")
        raise HTTPException(status_code=500, detail="Failed to add turn")
