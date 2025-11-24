from fastapi import APIRouter, Depends, HTTPException, Request, Form, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload
from typing import Optional
import json
from jose import JWTError
from datetime import timedelta

from ..database.database import session_pool, DatabaseConnectionError
from ..lib.auth import verify_password, create_access_token, build_token_payload
from ..lib.enums import UserRole
from ..models.user import User
from ..models.service_catalog import ServiceCatalog
from ..models.session import Session
from ..models.login_session import LoginSession
from ..utils.token import decodeJWT

router = APIRouter()
templates = Jinja2Templates(directory="templates")


async def require_admin(request: Request) -> User:
    """Dependency to require admin authentication - verifies JWT token from DB"""
    admin_token = request.cookies.get("admin_session")
    if not admin_token:
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})

    # Decode and verify JWT token
    try:
        payload = decodeJWT(admin_token)
        if not payload:
            raise HTTPException(status_code=302, headers={"Location": "/admin/login"})

        user_id = payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=302, headers={"Location": "/admin/login"})

        # Query database to get user and verify role
        try:
            async with session_pool() as db:
                result = await db.execute(select(User).where(User.id == user_id))
                user = result.scalar_one_or_none()

                if not user:
                    raise HTTPException(
                        status_code=302,
                        headers={"Location": "/admin/login"},
                    )

                # Verify user has ADMIN role from database
                if user.role != UserRole.ADMIN:
                    raise HTTPException(
                        status_code=403,
                        detail="Access denied. Admin privileges required.",
                    )

                return user
        except DatabaseConnectionError:
            raise HTTPException(
                status_code=503, detail="Database unavailable. Try again later."
            )
    except JWTError:
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})
    except Exception:
        raise HTTPException(status_code=302, headers={"Location": "/admin/login"})


@router.get("/login", response_class=HTMLResponse)
async def admin_login_page(request: Request):
    """Render admin login page"""
    return templates.TemplateResponse("admin_login.html", {"request": request})


@router.post("/login")
async def admin_login(request: Request):
    """Handle admin login"""
    # Get form data
    try:
        form_data = await request.form()
        email = form_data.get("email")
        password = form_data.get("password")

        if not email or not password:
            raise HTTPException(
                status_code=400, detail="Email and password are required"
            )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=400, detail=f"Failed to parse form data: {str(e)}"
        )

    try:
        async with session_pool() as db:
            # Find user by email
            result = await db.execute(select(User).where(User.email == email))
            user = result.scalar_one_or_none()

            if (
                not user
                or not user.password
                or not verify_password(password, user.password)
            ):
                raise HTTPException(status_code=401, detail="Invalid email or password")

            # Check if user is admin (verified from database)
            if user.role != UserRole.ADMIN:
                raise HTTPException(
                    status_code=403, detail="Access denied. Admin privileges required"
                )

            # Build JWT token payload with user data from database
            payload = await build_token_payload(user, db)

            # Create JWT access token for admin session
            access_token, expires_at = create_access_token(
                data=payload, expires_delta=timedelta(hours=8)
            )

    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Return HTMX redirect trigger
    response = HTMLResponse(
        content="",
        status_code=200,
        headers={"HX-Redirect": "/admin/dashboard"},
    )

    # Set secure JWT cookie
    response.set_cookie(
        key="admin_session",
        value=access_token,
        httponly=True,
        max_age=3600 * 8,  # 8 hours
        samesite="lax",
        # secure=True,  # Enable in production with HTTPS
    )

    return response


@router.post("/logout")
async def admin_logout():
    """Handle admin logout"""
    response = RedirectResponse(url="/admin/login", status_code=303)
    response.delete_cookie("admin_session")
    return response


@router.get("/dashboard", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    user: User = Depends(require_admin),
):
    """Render admin dashboard"""
    try:
        async with session_pool() as db:
            # Get statistics
            total_users = await db.scalar(select(func.count(User.id)))
            active_services = await db.scalar(
                select(func.count(ServiceCatalog.id)).where(
                    ServiceCatalog.is_active == True
                )
            )
            total_sessions = await db.scalar(select(func.count(Session.id)))
            active_sessions = await db.scalar(
                select(func.count(LoginSession.id)).where(
                    LoginSession.is_active == True
                )
            )

            stats = {
                "total_users": total_users or 0,
                "active_services": active_services or 0,
                "total_sessions": total_sessions or 0,
                "active_sessions": active_sessions or 0,
            }

    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")

    return templates.TemplateResponse(
        "admin_dashboard.html", {"request": request, "user": user, "stats": stats}
    )


@router.get("/dashboard/services", response_class=HTMLResponse)
async def admin_services_list(
    request: Request,
    user: User = Depends(require_admin),
):
    """Get services list"""
    try:
        async with session_pool() as db:
            result = await db.execute(
                select(ServiceCatalog).order_by(ServiceCatalog.id)
            )
            services = result.scalars().all()

        return templates.TemplateResponse(
            "admin_services.html", {"request": request, "services": services}
        )
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/dashboard/services/new", response_class=HTMLResponse)
async def admin_service_new_form(request: Request, user: User = Depends(require_admin)):
    """Render new service form"""
    return templates.TemplateResponse(
        "admin_service_form.html", {"request": request, "service": None}
    )


@router.get("/dashboard/services/{service_id}/edit", response_class=HTMLResponse)
async def admin_service_edit_form(
    request: Request,
    service_id: int,
    user: User = Depends(require_admin),
):
    """Render edit service form"""
    try:
        async with session_pool() as db:
            result = await db.execute(
                select(ServiceCatalog).where(ServiceCatalog.id == service_id)
            )
            service = result.scalar_one_or_none()

            if not service:
                raise HTTPException(status_code=404, detail="Service not found")

        return templates.TemplateResponse(
            "admin_service_form.html", {"request": request, "service": service}
        )
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.post("/dashboard/services", response_class=HTMLResponse)
async def admin_service_create(
    request: Request,
    name: str = Form(...),
    slug: str = Form(...),
    category: str = Form(...),
    provider: str = Form(...),
    default_config: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    user: User = Depends(require_admin),
):
    """Create new service"""
    # Parse default_config JSON
    config = None
    if default_config:
        try:
            config = json.loads(default_config)
        except json.JSONDecodeError:
            return HTMLResponse(
                content='<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">'
                "Invalid JSON in default_config"
                "</div>",
                status_code=400,
            )

    try:
        async with session_pool() as db:
            # Create service
            service = ServiceCatalog(
                name=name,
                slug=slug,
                category=category,
                provider=provider,
                default_config=config,
                is_active=is_active == "on",
            )

            db.add(service)
            await db.commit()
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Return updated services list
    return await admin_services_list(request, user)


@router.post("/dashboard/services/{service_id}", response_class=HTMLResponse)
async def admin_service_update(
    request: Request,
    service_id: int,
    name: str = Form(...),
    slug: str = Form(...),
    category: str = Form(...),
    provider: str = Form(...),
    default_config: Optional[str] = Form(None),
    is_active: Optional[str] = Form(None),
    user: User = Depends(require_admin),
):
    """Update service"""
    try:
        async with session_pool() as db:
            result = await db.execute(
                select(ServiceCatalog).where(ServiceCatalog.id == service_id)
            )
            service = result.scalar_one_or_none()

            if not service:
                raise HTTPException(status_code=404, detail="Service not found")

            # Parse default_config JSON
            config = None
            if default_config:
                try:
                    config = json.loads(default_config)
                except json.JSONDecodeError:
                    return HTMLResponse(
                        content='<div class="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">'
                        "Invalid JSON in default_config"
                        "</div>",
                        status_code=400,
                    )

            # Update service
            service.name = name
            service.slug = slug
            service.category = category
            service.provider = provider
            service.default_config = config
            service.is_active = is_active == "on"

            await db.commit()
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")

    # Return updated services list
    return await admin_services_list(request, user)


@router.delete("/dashboard/services/{service_id}")
async def admin_service_delete(
    service_id: int,
    user: User = Depends(require_admin),
):
    """Delete service"""
    try:
        async with session_pool() as db:
            result = await db.execute(
                select(ServiceCatalog).where(ServiceCatalog.id == service_id)
            )
            service = result.scalar_one_or_none()

            if not service:
                raise HTTPException(status_code=404, detail="Service not found")

            await db.delete(service)
            await db.commit()

        return HTMLResponse(content="", status_code=200)
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/dashboard/users", response_class=HTMLResponse)
async def admin_users_list(
    request: Request,
    user: User = Depends(require_admin),
):
    """Get users list"""
    try:
        async with session_pool() as db:
            result = await db.execute(select(User).order_by(User.id))
            users = result.scalars().all()

        return templates.TemplateResponse(
            "admin_users.html", {"request": request, "users": users}
        )
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")


@router.get("/dashboard/sessions", response_class=HTMLResponse)
async def admin_sessions_list(
    request: Request,
    user: User = Depends(require_admin),
):
    """Get sessions list"""
    try:
        async with session_pool() as db:
            result = await db.execute(
                select(LoginSession)
                .options(selectinload(LoginSession.user))
                .where(LoginSession.is_active == True)
                .order_by(LoginSession.created_at.desc())
            )
            sessions = result.scalars().all()

        return templates.TemplateResponse(
            "admin_sessions.html", {"request": request, "sessions": sessions}
        )
    except DatabaseConnectionError:
        raise HTTPException(status_code=503, detail="Database unavailable")
