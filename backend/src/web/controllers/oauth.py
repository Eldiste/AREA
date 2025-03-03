import logging

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.auth.config import decode_access_token, get_current_user
from src.config import get_db_async_session, settings
from src.db.models import Service, User, UserService

LOGGER = logging.getLogger(__name__)

router = APIRouter(prefix="/oauth", tags=["oauth"])

oauth = OAuth()
for provider_name, config in settings.oauth.providers.items():
    oauth.register(
        name=provider_name,
        client_id=config.client_id,
        client_secret=config.client_secret,
        api_base_url=config.api_base_url,
        access_token_url=config.token_url,
        authorize_url=config.authorize_url,
        redirect_uri=config.redirect_uri,
        client_kwargs={"scope": " ".join(config.scopes)},
    )


@router.get("/{provider}/login", status_code=302)
async def oauth_login(
    request: Request,
    provider: str,
    access_token: str,
    session: AsyncSession = Depends(get_db_async_session),
):
    if provider not in oauth._clients:
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Store the access token in the session for the callback
    request.session["user_access_token"] = access_token

    redirect_uri = settings.oauth.providers[provider].redirect_uri
    if not redirect_uri:
        raise HTTPException(
            status_code=500, detail=f"Redirect URI for {provider} is not configured."
        )

    return await oauth._clients[provider].authorize_redirect(request, redirect_uri)


@router.get("/{provider}/callback")
async def oauth_callback(
    request: Request,
    provider: str,
    session: AsyncSession = Depends(get_db_async_session),
):
    LOGGER.warning("Callback received for provider: %s", provider)

    if provider not in oauth._clients:
        LOGGER.error("Unsupported provider: %s", provider)
        raise HTTPException(status_code=400, detail="Unsupported provider")

    # Retrieve the access token from the session
    LOGGER.warning("Checking session for access token")
    LOGGER.warning("Session data: %s", dict(request.session))
    user_access_token = request.session.get("user_access_token")
    if not user_access_token:
        LOGGER.error("Access token not found in session")
        raise HTTPException(status_code=403, detail="Not authenticated")

    # Decode the JWT token to get the user
    LOGGER.warning("Attempting to decode access token")
    try:
        token_data = decode_access_token(user_access_token)
        LOGGER.warning("Decoded token data: %s", token_data)

        user_query = await session.execute(
            select(User).where(User.username == token_data.username)
        )
        current_user = user_query.scalar_one_or_none()

        if not current_user:
            LOGGER.error("User not found for username: %s", token_data.username)
            raise HTTPException(status_code=403, detail="User not found")
    except Exception as e:
        LOGGER.exception("Error decoding access token")
        raise HTTPException(status_code=403, detail="Invalid authentication token")

    # Get the OAuth2 token
    LOGGER.warning("Retrieving OAuth2 token from provider")
    token = await oauth._clients[provider].authorize_access_token(request)
    LOGGER.warning("Received OAuth2 token: %s", token)

    # Process service linkage
    LOGGER.warning("Fetching service data for provider: %s", provider)
    service_query = await session.execute(
        select(Service).where(Service.name == provider)
    )
    service = service_query.scalar_one_or_none()
    if not service:
        LOGGER.error("Service not found for provider: %s", provider)
        raise HTTPException(status_code=400, detail=f"Service {provider} not found")

    # Check and update the user's service linkage
    LOGGER.warning("Checking user service linkage")
    user_service_query = await session.execute(
        select(UserService)
        .where(UserService.user_id == current_user.id)
        .where(UserService.service_id == service.id)
    )
    user_service = user_service_query.scalar_one_or_none()

    if user_service:
        LOGGER.warning("Updating existing service linkage")
        user_service.access_token = token.get("access_token")
        user_service.refresh_token = token.get("refresh_token")
        user_service.updated_at = func.now()
    else:
        LOGGER.warning("Creating new service linkage")
        user_service = UserService(
            user_id=current_user.id,
            service_id=service.id,
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
        )
        session.add(user_service)

    await session.commit()
    request.session.pop("user_access_token", None)

    frontend_url = settings.frontend_url
    LOGGER.warning("Redirecting to frontend: %s", frontend_url)
    return RedirectResponse(url=f"{frontend_url}/#/home/")
