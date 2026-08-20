import asyncio
import logging
import secrets
from datetime import datetime
from typing import Optional

import httpx
import pydantic
from fastapi import Cookie, Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import APIKeyCookie
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

import json_endpoints

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
    authenticated = request.cookies.get("tapistoken") is not None
    return templates.TemplateResponse(
        request=request,
        name="root.old.html",
        context={
            "tenant_id": settings.TAPIS_TENANT_URL,
            "authenticated": authenticated,
        },
    )


@app.get("/login")
async def login() -> RedirectResponse:
    AUTH_STATE = secrets.token_hex(24)
    OAUTH_REDIRECT_URL = (
        f"{settings.TAPIS_TENANT_URL}/v3/oauth2/authorize"
        f"?client_id={settings.TAPIS_OAUTH_CLIENT_ID}"
        f"&redirect_uri={settings.TAPIS_OAUTH_CALLBACK_URL}"
        f"&response_type=code&state={AUTH_STATE}"
    )
    redirect_response = RedirectResponse(OAUTH_REDIRECT_URL)

    # Set a state cookie to check at the end of the OAuth flow.
    redirect_response.set_cookie("AUTH_STATE", AUTH_STATE, httponly=True)
    return redirect_response


@app.get("/oauth-callback")
async def oauth_callback(
    state: Optional[str] = None,  # HTTP query param
    code: Optional[str] = None,  # HTTP query param
    initial_state: Optional[str] = Cookie(alias="AUTH_STATE"),
) -> RedirectResponse:
    # Check that the state returned from OAuth is the same secret we set at the start
    if not state == initial_state:
        raise HTTPException(status.HTTP_403_FORBIDDEN, detail="state mismatch")

    # Exchange the authorization code for a Tapis JWT
    token_claim_response = httpx.post(
        f"{settings.TAPIS_TENANT_URL}/v3/oauth2/tokens",
        data={
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": settings.TAPIS_OAUTH_CALLBACK_URL,
        },
        auth=(settings.TAPIS_OAUTH_CLIENT_ID, settings.TAPIS_OAUTH_CLIENT_KEY),
    )
    token_claim_json = token_claim_response.json()
    token_result = TokenResult.model_validate(token_claim_json.get("result", {}))

    # Redirect to home page and set access/refresh tokens as cookies.
    redirect_response = RedirectResponse("/")
    redirect_response.set_cookie(
        "tapistoken",
        value=token_result.access_token.access_token,
        expires=token_result.access_token.expires_at,
        samesite="lax",
    )
    redirect_response.set_cookie(
        "refreshtoken",
        value=token_result.refresh_token.refresh_token,
        httponly=True,  # Prevent refresh token from being exfiltrated (XSS attack)
        samesite="strict",  # Prevent refresh token from being used in a request from another site (CSRF attack)
        expires=token_result.refresh_token.expires_at,
    )
    redirect_response.delete_cookie("AUTH_STATE")
    return redirect_response


async def revoke_token(client: httpx.AsyncClient, token: str) -> None:
    resp = await client.post(
        f"{settings.TAPIS_TENANT_URL}/v3/tokens/revoke", json={"token": token}
    )
    resp.raise_for_status()
    logger.info(resp.json())


async def revoke_tokens(tokens: list[str]) -> None:
    async with httpx.AsyncClient() as client:
        async with asyncio.TaskGroup() as tg:
            for token in tokens:
                tg.create_task(revoke_token(client, token))


@app.get("/logout")
async def logout(
    tapis_token=Depends(APIKeyCookie(name="tapistoken")),
    refresh_token=Depends(APIKeyCookie(name="refreshtoken")),
) -> RedirectResponse:
    """
    Revoke tokens and log the user out.
    """
    await revoke_tokens([tapis_token, refresh_token])

    redirect_response = RedirectResponse("/")
    redirect_response.delete_cookie("tapistoken")
    redirect_response.delete_cookie("refreshtoken")
    return redirect_response


@app.get("/whoami")
async def whoami(
    request: Request, tapis_token: str = Depends(APIKeyCookie(name="tapistoken"))
) -> HTMLResponse:
    user_info = httpx.get(
        f"{settings.TAPIS_TENANT_URL}/v3/oauth2/userinfo",
        headers={"x-tapis-token": tapis_token},
    )

    return templates.TemplateResponse(
        request=request,
        name="whoami.html",
        context=user_info.json()["result"],
    )


@app.get("/systems")
async def get_systems(
    request: Request, tapis_token: str = Depends(APIKeyCookie(name="tapistoken"))
) -> HTMLResponse:
    system_info = httpx.get(
        f"{settings.TAPIS_TENANT_URL}/v3/systems",
        headers={"x-tapis-token": tapis_token},
    )
    return templates.TemplateResponse(
        request=request,
        name="systems.html",
        context={"systems": system_info.json()["result"]},
    )


@app.get("/files/{system}")
async def get_files(
    system: str,
    request: Request,
    tapis_token: str = Depends(APIKeyCookie(name="tapistoken")),
) -> HTMLResponse:
    file_info = httpx.get(
        f"{settings.TAPIS_TENANT_URL}/v3/files/ops/{system}/",
        headers={"x-tapis-token": tapis_token},
    )
    return templates.TemplateResponse(
        request=request,
        name="file-listing-offcanvas.html",
        context={"files": file_info.json()["result"], "system": system},
    )
