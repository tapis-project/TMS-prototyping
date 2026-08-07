import asyncio
import logging
import secrets
from datetime import datetime
from typing import Optional

import httpx
import pydantic
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.security import APIKeyCookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json_endpoints
from urllib.parse import urlencode

import settings

logger = logging.getLogger("uvicorn.info")
app = FastAPI()
app.include_router(json_endpoints.router)

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


class AccessToken(pydantic.BaseModel):
    access_token: str
    expires_at: datetime
    expires_in: int
    id_token: str


class RefreshToken(pydantic.BaseModel):
    expires_at: datetime
    expires_in: int
    jti: str
    refresh_token: str


class TokenResult(pydantic.BaseModel):
    access_token: AccessToken
    refresh_token: RefreshToken


@app.get("/")
async def root(request: Request) -> HTMLResponse:
    authenticated = request.cookies.get("globustoken") is not None
    user_info = None
    if authenticated:
        user_info_resp = httpx.get(
            "https://auth.globus.org/v2/oauth2/userinfo",
            headers={"Authorization": f"Bearer {request.cookies.get("globustoken")}"},
        )
        user_info = user_info_resp.json()
    print(user_info)
    return templates.TemplateResponse(
        request=request,
        name="root_globus.html",
        context={
            "user_info": user_info,
            "tenant_id": settings.TAPIS_TENANT_URL,
            "authenticated": authenticated,
        },
    )


@app.get("/login")
async def login() -> RedirectResponse:
    AUTH_STATE = secrets.token_hex(24)
    # OAUTH_REDIRECT_URL = (
    #     f"{settings.GLOBUS_OAUTH_URL}/v2/oauth2/authorize"
    #     f"?client_id=fb313bae-4dd0-4a5d-a43e-a9b89a0917ec"
    #     "&redirect_uri=http://localhost:8000/oauth-callback"
    #     "&scope=openid email profile"
    #     f"&response_type=code&state={AUTH_STATE}"
    # )
    OAUTH_REDIRECT_URL = (
        f"{settings.GLOBUS_OAUTH_URL}/v2/oauth2/authorize"
        f"?client_id=fb313bae-4dd0-4a5d-a43e-a9b89a0917ec"
        "&redirect_uri=http://localhost:8000/oauth-callback"
        "&scope=openid email profile offline_access"
        f"&response_type=code&state={AUTH_STATE}"
    )
    redirect_response = RedirectResponse(OAUTH_REDIRECT_URL)

    # Set a state cookie to check at the end of the OAuth flow.
    redirect_response.set_cookie("AUTH_STATE", AUTH_STATE, httponly=True)
    return redirect_response


@app.get("/oauth-callback")
async def oauth_callback(
    request: Request,
    state: Optional[str] = None,  # HTTP query param
    code: Optional[str] = None,  # HTTP query param
    initial_state: Optional[str] = Cookie(alias="AUTH_STATE"),
) -> RedirectResponse:
    # Check that the state returned from OAuth is the same secret we set at the start

    print(state)
    print(code)

    if not state == initial_state:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="state mismatch")

    # Exchange the authorization code for a Tapis JWT
    token_claim_response = httpx.post(
        "https://auth.globus.org/v2/oauth2/token",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "http://localhost:8000/oauth-callback",
        },
        auth=(settings.GLOBUS_OAUTH_CLIENT_ID, settings.GLOBUS_OAUTH_CLIENT_SECRET),
    )

    token_json = token_claim_response.json()
    print(token_json)

    # Redirect to home page and set access/refresh tokens as cookies.
    redirect_response = RedirectResponse("/")
    redirect_response.set_cookie(
        "globustoken",
        value=token_json["access_token"],
        max_age=token_json["expires_in"],
        samesite="lax",
    )

    redirect_response.delete_cookie("AUTH_STATE")
    return redirect_response


class PostResponse(pydantic.BaseModel):
    code: str


@app.post("/oauth-proxy")
async def oauth_proxy(
    input: PostResponse,  # HTTP query param
) -> JSONResponse:
    # Check that the state returned from OAuth is the same secret we set at the start

    return {"code": input.code + "OK2"}


# async def revoke_token(client: httpx.AsyncClient, token: str) -> None:
#     resp = await client.post(
#         f"{settings.TAPIS_TENANT_URL}/v3/tokens/revoke", json={"token": token}
#     )
#     resp.raise_for_status()
#     logger.info(resp.json())


async def revoke_tokens(tokens: list[str]) -> None:
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            for token in tokens:
                tg.create_task(revoke_token(client, token))


# @app.get("/logout")
# async def logout(
#     tapis_token=Depends(APIKeyCookie(name="tapistoken")),
#     refresh_token=Depends(APIKeyCookie(name="refreshtoken")),
# ) -> RedirectResponse:
#     """
#     Revoke tokens and log the user out.
#     """
#     await revoke_tokens([tapis_token, refresh_token])

#     redirect_response = RedirectResponse("/")
#     redirect_response.delete_cookie("tapistoken")
#     redirect_response.delete_cookie("refreshtoken")
#     return redirect_response


async def revoke_token(client: httpx.AsyncClient, token: str) -> None:
    resp = await client.post(
        f"{settings.GLOBUS_OAUTH_URL}/v2/oauth2/token/revoke",
        data={"token": token},   # form-encoded, not json=
        auth=(settings.GLOBUS_OAUTH_CLIENT_ID, settings.GLOBUS_OAUTH_CLIENT_SECRET),
    )
    resp.raise_for_status()
    logger.info(resp.json())


GLOBUS_LOGOUT_URL = f"{settings.GLOBUS_OAUTH_URL}/v2/web/logout?" + urlencode({
    "client_id": settings.GLOBUS_OAUTH_CLIENT_ID,
    "redirect_uri": "http://localhost:8000/",
    "redirect_name": "My App",
})


@app.get("/logout")
async def logout(
    globus_token: Optional[str] = Cookie(default=None, alias="globustoken"),
    refresh_token: Optional[str] = Cookie(default=None, alias="refreshtoken"),
) -> RedirectResponse:
    """Revoke tokens and log the user out."""
    try:
        await revoke_tokens([globus_token, refresh_token])
    except Exception:
        logger.exception("token revocation failed; clearing cookies anyway")

    # resp = RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)
    resp = RedirectResponse(GLOBUS_LOGOUT_URL, status_code=status.HTTP_303_SEE_OTHER)
    resp.delete_cookie("globustoken", samesite="lax", path="/")
    resp.delete_cookie("refreshtoken", samesite="lax", path="/")
    return resp
