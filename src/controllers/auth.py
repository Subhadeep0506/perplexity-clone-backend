from authlib.integrations.httpx_client import AsyncOAuth2Client
from sqlalchemy import select
from datetime import datetime
from fastapi import HTTPException, Request
import os
from ..database.database import session_pool
from ..models.user import User
from ..models.profile import Profile
from ..models.login_session import LoginSession
from ..models.session import Session
from ..models.user_settings import UserSettings
from ..schemas.auth import RegisterRequest, LoginRequest
from ..lib.auth import (
    hash_password,
    verify_password,
    create_access_token,
    create_refresh_token,
    store_token_in_session,
)
from ..services.logger import SingletonLogger


async def register_user(register_data: RegisterRequest):
    """Register a new user with email and password"""
    async with session_pool() as session:
        # Check if email already exists
        result = await session.execute(
            select(User).where(User.email == register_data.email)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Email already registered")

        # Check if username already exists
        result = await session.execute(
            select(User).where(User.username == register_data.username)
        )
        if result.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Username already taken")

        # Create new user
        hashed_password = hash_password(register_data.password)
        user = User(
            username=register_data.username,
            full_name=register_data.full_name,
            email=register_data.email,
            password=hashed_password,
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)

        # Create default profile and settings for the new user
        profile = Profile(user_id=user.id)
        user_settings = UserSettings(user_id=user.id)
        session.add_all([profile, user_settings])
        await session.commit()

        return {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "full_name": user.full_name,
        }


async def login_user(login_data: LoginRequest, request: Request):
    """Authenticate user with email and password"""
    async with session_pool() as session:
        # Find user by email
        result = await session.execute(
            select(User).where(User.email == login_data.email)
        )
        user = result.scalar_one_or_none()

        if not user or not user.password:
            raise HTTPException(status_code=401, detail="Invalid credentials")
        if not verify_password(login_data.password, user.password):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # Create tokens
        access_token, token_expires_at = create_access_token(data={"sub": str(user.id)})
        refresh_token = create_refresh_token(subject=str(user.id))

        # Store tokens in login session
        login_session = await store_token_in_session(
            session=session,
            user_id=user.id,
            access_token=access_token,
            refresh_token=refresh_token,
            login_method="password",
            device_info=(
                request.headers.get("sec-ch-ua-platform", "").strip('"')
                if request.headers.get("sec-ch-ua-platform")
                else None
            ),
            ip_address=request.client.host if request.client else None,
            user_agent=request.headers.get("user-agent"),
            token_expires_at=token_expires_at,
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
            "expires_in": int((token_expires_at - datetime.utcnow()).total_seconds()),
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "full_name": user.full_name,
            },
        }


oauth = AsyncOAuth2Client(
    client_id=os.getenv("GOOGLE_CLIENT_ID"),
    client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
    redirect_uri=os.getenv("GOOGLE_REDIRECT_URI"),
    authorize_url="https://accounts.google.com/o/oauth2/auth",
    access_token_url="https://oauth2.googleapis.com/token",
    userinfo_url="https://www.googleapis.com/oauth2/v2/userinfo",
)


async def initiate_google_login():
    """Generate Google OAuth authorization URL"""
    authorization_url, state = oauth.create_authorization_url(
        "https://accounts.google.com/o/oauth2/auth",
        scope=["openid", "email", "profile"],
    )
    return {"authorization_url": authorization_url, "state": state}


async def handle_google_callback(code: str, state: str, request: Request):
    """Process Google OAuth callback and authenticate/create user"""
    try:
        token = await oauth.fetch_token(
            "https://oauth2.googleapis.com/token",
            code=code,
        )

        user_info = await oauth.get("https://www.googleapis.com/oauth2/v2/userinfo")
        user_data = user_info.json()

        async with session_pool() as session:
            result = await session.execute(
                select(User).where(User.google_id == user_data["id"])
            )
            user = result.scalar_one_or_none()

            if not user:
                result = await session.execute(
                    select(User).where(User.email == user_data["email"])
                )
                user = result.scalar_one_or_none()

                if user:
                    user.google_id = user_data["id"]
                else:
                    username = user_data["email"].split("@")[0]
                    existing = await session.execute(
                        select(User).where(User.username == username)
                    )
                    if existing.scalar_one_or_none():
                        username = f"{username}_{user_data['id']}"

                    user = User(
                        username=username,
                        full_name=user_data["name"],
                        email=user_data["email"],
                        google_id=user_data["id"],
                    )
                    session.add(user)
                    await session.commit()
                    await session.refresh(user)

                    # Create default profile and settings for the new Google user
                    profile = Profile(user_id=user.id)
                    user_settings = UserSettings(user_id=user.id)
                    session.add_all([profile, user_settings])
                    await session.commit()
            # Create tokens
            access_token, token_expires_at = create_access_token(
                data={"sub": str(user.id)}
            )
            refresh_token, _ = create_refresh_token(subject=str(user.id))

            # Store tokens in login session
            login_session = await store_token_in_session(
                session=session,
                user_id=user.id,
                access_token=access_token,
                refresh_token=refresh_token,
                login_method="google",
                device_info=(
                    request.headers.get("sec-ch-ua-platform", "").strip('"')
                    if request.headers.get("sec-ch-ua-platform")
                    else None
                ),
                ip_address=request.client.host if request.client else None,
                user_agent=request.headers.get("user-agent"),
                token_expires_at=token_expires_at,
            )

            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": int(
                    (token_expires_at - datetime.utcnow()).total_seconds()
                ),
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "full_name": user.full_name,
                },
            }

    except Exception as e:
        logger = getattr(request.app.state, "logger", SingletonLogger().get_logger())
        logger.error(f"OAuth error: {e}")
        raise HTTPException(status_code=400, detail=f"OAuth error: {str(e)}")


async def logout_user(user_id: int, session_id: int | None = None):
    """Logout user by deactivating login session(s)"""
    async with session_pool() as session:
        if session_id:
            result = await session.execute(
                select(LoginSession).where(
                    LoginSession.id == session_id,
                    LoginSession.user_id == user_id,
                    LoginSession.is_active == True,
                )
            )
            login_session = result.scalar_one_or_none()
            if login_session:
                login_session.is_active = False
                login_session.logout_at = datetime.utcnow()
                await session.commit()
                return {"message": "Logged out successfully"}
            else:
                raise HTTPException(status_code=404, detail="Active session not found")
        else:
            result = await session.execute(
                select(LoginSession).where(
                    LoginSession.user_id == user_id, LoginSession.is_active == True
                )
            )
            login_sessions = result.scalars().all()
            for ls in login_sessions:
                ls.is_active = False
                ls.logout_at = datetime.utcnow()
            await session.commit()
            return {"message": f"Logged out from {len(login_sessions)} sessions"}


async def get_user_sessions(user_id: int):
    """Get all login sessions for a user"""
    async with session_pool() as session:
        result = await session.execute(
            select(LoginSession)
            .where(LoginSession.user_id == user_id)
            .order_by(LoginSession.created_at.desc())
        )
        sessions = result.scalars().all()
        return [
            {
                "id": s.id,
                "login_method": s.login_method,
                "is_active": s.is_active,
                "created_at": s.created_at,
                "logout_at": s.logout_at,
                "device_info": s.device_info,
                "ip_address": s.ip_address,
            }
            for s in sessions
        ]


async def delete_user_account(user_id: int):
    """Delete a user account and all associated data"""
    async with session_pool() as session:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        # Delete the user (cascade will handle related records)
        await session.delete(user)
        await session.commit()
        return {"message": "User account deleted successfully"}
