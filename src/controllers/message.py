"""Controller for Message CRUD operations."""

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError
from fastapi import HTTPException
from ..database.database import session_pool, DatabaseConnectionError
from ..models.message import Message
from ..schemas.message import (
    MessageCreate,
    MessageUpdate,
    MessageResponse,
)
from ..services.logger import SingletonLogger

logger = SingletonLogger().get_logger()


async def list_messages(
    session_id: int | None = None, user_id: int | None = None
) -> list[MessageResponse]:
    """List messages in batch, filterable by session_id or user_id."""
    try:
        async with session_pool() as session:
            stmt = select(Message)
            if session_id is not None:
                stmt = stmt.where(Message.session_id == session_id)
            if user_id is not None:
                stmt = stmt.where(Message.user_id == user_id)
            result = await session.execute(stmt)
            messages = result.scalars().all()
            return [MessageResponse.from_orm(m) for m in messages]
    except DBAPIError as e:
        logger.exception(f"Database connection error listing messages: {str(e)}")
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error listing messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list messages")
    except Exception as e:
        logger.error(f"Unexpected error listing messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_message(message_data: MessageCreate) -> MessageResponse:
    try:
        async with session_pool() as session:
            new_msg = Message(
                session_id=message_data.session_id,
                user_id=message_data.user_id,
                content=message_data.content,
                parent_message_id=message_data.parent_message_id,
                model_used=message_data.model_used,
                confidence_score=message_data.confidence_score,
            )
            session.add(new_msg)
            await session.commit()
            await session.refresh(new_msg)
            return MessageResponse.from_orm(new_msg)
    except IntegrityError as e:
        logger.error(f"Integrity error creating message: {str(e)}")
        raise HTTPException(
            status_code=400, detail="Failed to create message due to data constraint"
        )
    except DBAPIError as e:
        logger.exception(f"Database connection error creating message: {str(e)}")
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create message")
    except Exception as e:
        logger.error(f"Unexpected error creating message: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def update_message(
    message_id: int, message_data: MessageUpdate
) -> MessageResponse:
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(Message).where(Message.id == message_id)
            )
            msg = result.scalar_one_or_none()
            if not msg:
                raise HTTPException(status_code=404, detail="Message not found")

            update_data = message_data.model_dump(exclude_unset=True)
            for field, value in update_data.items():
                setattr(msg, field, value)

            await session.commit()
            await session.refresh(msg)
            return MessageResponse.from_orm(msg)
    except HTTPException:
        raise
    except DBAPIError as e:
        logger.exception(
            f"Database connection error updating message id={message_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error updating message id={message_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to update message")
    except Exception as e:
        logger.error(f"Unexpected error updating message id={message_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_messages(message_ids: list[int]) -> dict:
    """Delete messages in batch by IDs."""
    if not message_ids:
        raise HTTPException(
            status_code=400, detail="No message IDs provided for deletion"
        )
    try:
        async with session_pool() as session:
            await session.execute(delete(Message).where(Message.id.in_(message_ids)))
            await session.commit()
            return {"deleted": True}
    except DBAPIError as e:
        logger.exception(f"Database connection error deleting messages: {str(e)}")
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete messages")
    except Exception as e:
        logger.error(f"Unexpected error deleting messages: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
