"""Controller for Session CRUD operations."""

from sqlalchemy import select, delete
from sqlalchemy.exc import SQLAlchemyError, DBAPIError, IntegrityError
from fastapi import HTTPException
from ..database.database import session_pool, DatabaseConnectionError
from ..models.session import Session
from ..schemas.session import (
    SessionCreate,
    SessionUpdate,
    SessionResponse,
)
from ..services.logger import SingletonLogger

logger = SingletonLogger().get_logger()


async def get_sessions_for_user(user_id: int) -> list[SessionResponse]:
    try:
        async with session_pool() as session:
            result = await session.execute(
                select(Session).where(Session.user_id == user_id)
            )
            sessions = result.scalars().all()
            return [SessionResponse.from_orm(s) for s in sessions]
    except DBAPIError as e:
        logger.exception(
            f"Database connection error fetching sessions for user_id={user_id}: {str(e)}"
        )
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(
            f"Database error fetching sessions for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Failed to retrieve sessions")
    except Exception as e:
        logger.error(
            f"Unexpected error fetching sessions for user_id={user_id}: {str(e)}"
        )
        raise HTTPException(status_code=500, detail="Internal server error")


async def create_session(session_data: SessionCreate) -> SessionResponse:
    try:
        async with session_pool() as session:
            new_session = Session(
                user_id=session_data.user_id,
                started_at=session_data.started_at,
                ended_at=session_data.ended_at,
                device_type=session_data.device_type,
            )
            session.add(new_session)
            await session.commit()
            await session.refresh(new_session)
            return SessionResponse.from_orm(new_session)
    except IntegrityError as e:
        logger.error(
            f"Integrity error creating session for user_id={session_data.user_id}: {str(e)}"
        )
        raise HTTPException(
            status_code=400, detail="Failed to create session due to data constraint"
        )
    except DBAPIError as e:
        logger.exception(f"Database connection error creating session: {str(e)}")
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create session")
    except Exception as e:
        logger.error(f"Unexpected error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")


async def delete_sessions(
    user_id: int | None = None, session_ids: list[int] | None = None
) -> dict:
    """Delete sessions in batch either by user_id (delete all for user) or by a list of session_ids."""
    if not user_id and not session_ids:
        raise HTTPException(
            status_code=400, detail="Provide user_id or session_ids to delete"
        )
    try:
        async with session_pool() as session:
            if session_ids:
                await session.execute(
                    delete(Session).where(Session.id.in_(session_ids))
                )
            else:
                await session.execute(delete(Session).where(Session.user_id == user_id))
            await session.commit()
            return {"deleted": True}
    except DBAPIError as e:
        logger.exception(f"Database connection error deleting sessions: {str(e)}")
        raise DatabaseConnectionError(str(e))
    except SQLAlchemyError as e:
        logger.error(f"Database error deleting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to delete sessions")
    except Exception as e:
        logger.error(f"Unexpected error deleting sessions: {str(e)}")
        raise HTTPException(status_code=500, detail="Internal server error")
