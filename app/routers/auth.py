from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from jose import jwt, JWTError

from app.models import UserCreate, User, Token, UserResponse
from app.security import (
    get_password_hash, authenticate_user, create_access_token,
    create_refresh_token, SECRET_KEY, ALGORITHM
)
from app.database import get_user_collection

router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/register", response_model=UserResponse)
async def register_user(user: UserCreate):
    user_collection = await get_user_collection()

    existing_user = await user_collection.find_one({"username": user.username})
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already registered"
        )

    existing_email = await user_collection.find_one({"email": user.email})
    if existing_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )

    last_user = await user_collection.find_one({}, sort=[("id", -1)])
    new_id = 1 if not last_user else last_user["id"] + 1

    hashed_password = get_password_hash(user.password)
    user_dict = {
        "id": new_id,
        "username": user.username,
        "email": user.email,
        "hashed_password": hashed_password,
        "disabled": False
    }

    await user_collection.insert_one(user_dict)
    return {k: v for k, v in user_dict.items() if k != "hashed_password"}

@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = await authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token, access_token_expires_at = create_access_token(user.username)
    refresh_token, refresh_token_expires_at = create_refresh_token(user.username)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "access_token_expires_at": access_token_expires_at,
        "refresh_token_expires_at": refresh_token_expires_at
    }


@router.post("/refresh", response_model=Token)
async def refresh_token(refresh_token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        token_type = payload.get("token_type")

        if username is None or token_type != "refresh":
            raise credentials_exception

        access_token, access_token_expires_at = create_access_token(username)
        new_refresh_token, refresh_token_expires_at = create_refresh_token(username)

        return {
            "access_token": access_token,
            "refresh_token": new_refresh_token,
            "token_type": "bearer",
            "access_token_expires_at": access_token_expires_at,
            "refresh_token_expires_at": refresh_token_expires_at
        }
    except JWTError:
        raise credentials_exception