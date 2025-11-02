import httpx
from fastapi import HTTPException, status
from app.config import settings
from app.schemas.auth import GoogleUserInfo


async def get_google_user_info(access_token: str) -> GoogleUserInfo:
    """Получает информацию о пользователе от Google API"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                "https://www.googleapis.com/oauth2/v2/userinfo",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            response.raise_for_status()
            user_info = response.json()
            
            return GoogleUserInfo(
                id=user_info["id"],
                email=user_info["email"],
                name=user_info["name"],
                picture=user_info.get("picture"),
                verified_email=user_info.get("verified_email", False)
            )
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to get user info from Google: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error getting user info: {str(e)}"
            )


async def exchange_code_for_token(code: str) -> str:
    """Обменивает код авторизации на access token"""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                "https://oauth2.googleapis.com/token",
                data={
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "code": code,
                    "grant_type": "authorization_code",
                    "redirect_uri": settings.google_redirect_uri,
                }
            )
            response.raise_for_status()
            token_data = response.json()
            return token_data["access_token"]
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Failed to exchange code for token: {e.response.text}"
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error exchanging code for token: {str(e)}"
            )
