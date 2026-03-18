"""
Asklytics: Supabase client initialization and utilities.
Wraps the Supabase Python client for PostgreSQL + Auth operations.
"""
import logging
from supabase import create_client, Client
from app.config import get_settings

logger = logging.getLogger(__name__)

# Global Supabase client (lazy-loaded)
_supabase_client: Client = None


def get_supabase_client() -> Client:
    """
    Get or initialize the Supabase client.
    Uses lru_cache-style lazy loading.
    """
    global _supabase_client

    if _supabase_client is None:
        settings = get_settings()

        if not settings.supabase_url:
            raise ValueError("SUPABASE_URL not set in .env")
        if not settings.supabase_key:
            raise ValueError("SUPABASE_KEY not set in .env")

        try:
            _supabase_client = create_client(
                settings.supabase_url,
                settings.supabase_key
            )
            logger.info("✓ Supabase client initialized")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Supabase client: {e}")
            raise

    return _supabase_client


def close_supabase_client() -> None:
    """Close Supabase client connection (if needed)."""
    global _supabase_client
    if _supabase_client is not None:
        _supabase_client = None
        logger.info("Supabase client closed")


# ============================================================================
# PROFILE OPERATIONS
# ============================================================================

async def create_profile(
    user_id: str,
    email: str,
    full_name: str = None,
    avatar_url: str = None
) -> dict:
    """
    Create a user profile in Supabase.

    Args:
        user_id: UUID from Supabase Auth
        email: User email
        full_name: Optional full name
        avatar_url: Optional avatar URL

    Returns:
        Profile dict from database
    """
    client = get_supabase_client()

    try:
        response = client.table("profiles").insert({
            "id": user_id,
            "email": email,
            "full_name": full_name,
            "avatar_url": avatar_url
        }).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating profile: {e}")
        raise


async def get_profile(user_id: str) -> dict:
    """Get user profile by ID."""
    client = get_supabase_client()

    try:
        response = client.table("profiles").select("*").eq("id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        raise


async def update_profile(
    user_id: str,
    full_name: str = None,
    avatar_url: str = None
) -> dict:
    """Update user profile."""
    client = get_supabase_client()

    update_data = {}
    if full_name is not None:
        update_data["full_name"] = full_name
    if avatar_url is not None:
        update_data["avatar_url"] = avatar_url

    if not update_data:
        return await get_profile(user_id)

    try:
        response = client.table("profiles").update(update_data).eq("id", user_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise


# ============================================================================
# CONVERSATION OPERATIONS
# ============================================================================

async def create_conversation(
    user_id: str,
    title: str = None,
    datasource_id: str = "default"
) -> dict:
    """
    Create a new conversation.

    Args:
        user_id: UUID of the user
        title: Optional conversation title (auto-generated from first query if None)
        datasource_id: Data source ID (default or custom CSV upload ID)

    Returns:
        Conversation dict with id, user_id, created_at, etc.
    """
    client = get_supabase_client()

    try:
        response = client.table("conversations").insert({
            "user_id": user_id,
            "title": title,
            "datasource_id": datasource_id
        }).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise


async def get_conversation(conversation_id: str) -> dict:
    """
    Get single conversation with all its turns.

    Args:
        conversation_id: UUID of conversation

    Returns:
        Conversation dict with nested turns array
    """
    client = get_supabase_client()

    try:
        response = client.table("conversations").select(
            "*, conversation_turns(id, turn_number, user_prompt, sql_generated, charts, insight_summary, data_limitations, execution_time_ms, created_at)"
        ).eq("id", conversation_id).execute()

        if response.data:
            conversation = response.data[0]
            # Rename nested turns key if needed
            if "conversation_turns" in conversation:
                conversation["turns"] = conversation.pop("conversation_turns")
            return conversation
        return None
    except Exception as e:
        logger.error(f"Error fetching conversation: {e}")
        raise


async def list_conversations(user_id: str, limit: int = 50, offset: int = 0) -> list:
    """
    List all conversations for a user (most recent first).

    Args:
        user_id: UUID of user
        limit: Max results (default 50)
        offset: Pagination offset

    Returns:
        List of conversation dicts with turn count
    """
    client = get_supabase_client()

    try:
        # Get conversation count per conversation
        response = client.table("conversations").select(
            "id, title, created_at, updated_at, conversation_turns(count)"
        ).eq("user_id", user_id).order("updated_at", desc=True).range(offset, offset + limit - 1).execute()

        conversations = response.data if response.data else []

        # Flatten turn counts
        for conv in conversations:
            if "conversation_turns" in conv and conv["conversation_turns"]:
                conv["turn_count"] = len(conv["conversation_turns"])
            else:
                conv["turn_count"] = 0
            conv.pop("conversation_turns", None)

        return conversations
    except Exception as e:
        logger.error(f"Error listing conversations: {e}")
        raise


async def update_conversation_title(conversation_id: str, title: str) -> dict:
    """Update conversation title."""
    client = get_supabase_client()

    try:
        response = client.table("conversations").update({
            "title": title
        }).eq("id", conversation_id).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise


async def delete_conversation(conversation_id: str) -> None:
    """Delete entire conversation (cascades to turns)."""
    client = get_supabase_client()

    try:
        client.table("conversations").delete().eq("id", conversation_id).execute()
    except Exception as e:
        logger.error(f"Error deleting conversation: {e}")
        raise


# ============================================================================
# CONVERSATION TURN OPERATIONS
# ============================================================================

async def add_conversation_turn(
    conversation_id: str,
    user_prompt: str,
    sql_generated: str = None,
    charts: dict = None,
    insight_summary: str = None,
    data_limitations: str = None,
    execution_time_ms: int = None
) -> dict:
    """
    Add a turn to a conversation.

    Args:
        conversation_id: UUID of parent conversation
        user_prompt: The user's question
        sql_generated: The SQL that was generated and executed
        charts: The chart specifications and data
        insight_summary: AI-generated insight (grounded in real data)
        data_limitations: Limitations of the data/analysis
        execution_time_ms: Query execution time

    Returns:
        Turn dict with id, turn_number, created_at, etc.
    """
    client = get_supabase_client()

    try:
        # Get next turn number for this conversation
        turns_response = client.table("conversation_turns").select(
            "turn_number"
        ).eq("conversation_id", conversation_id).order("turn_number", desc=True).limit(1).execute()

        next_turn_number = 1
        if turns_response.data:
            next_turn_number = turns_response.data[0]["turn_number"] + 1

        # Insert new turn
        response = client.table("conversation_turns").insert({
            "conversation_id": conversation_id,
            "turn_number": next_turn_number,
            "user_prompt": user_prompt,
            "sql_generated": sql_generated,
            "charts": charts,
            "insight_summary": insight_summary,
            "data_limitations": data_limitations,
            "execution_time_ms": execution_time_ms
        }).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error adding conversation turn: {e}")
        raise


async def get_conversation_turn(turn_id: int) -> dict:
    """Get a single conversation turn by ID."""
    client = get_supabase_client()

    try:
        response = client.table("conversation_turns").select("*").eq("id", turn_id).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching turn: {e}")
        raise


# ============================================================================
# SESSION OPERATIONS
# ============================================================================

async def create_session(user_id: str, refresh_token: str, expires_at: str) -> dict:
    """
    Create a session with refresh token.

    Args:
        user_id: UUID of user
        refresh_token: The refresh token string
        expires_at: ISO 8601 timestamp when session expires

    Returns:
        Session dict with id, created_at, expires_at
    """
    client = get_supabase_client()

    try:
        response = client.table("sessions").insert({
            "user_id": user_id,
            "refresh_token": refresh_token,
            "expires_at": expires_at
        }).execute()

        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error creating session: {e}")
        raise


async def get_session_by_refresh_token(refresh_token: str) -> dict:
    """Get session by refresh token."""
    client = get_supabase_client()

    try:
        response = client.table("sessions").select("*").eq("refresh_token", refresh_token).execute()
        return response.data[0] if response.data else None
    except Exception as e:
        logger.error(f"Error fetching session: {e}")
        raise


async def delete_session(session_id: str) -> None:
    """Delete a session."""
    client = get_supabase_client()

    try:
        client.table("sessions").delete().eq("id", session_id).execute()
    except Exception as e:
        logger.error(f"Error deleting session: {e}")
        raise
