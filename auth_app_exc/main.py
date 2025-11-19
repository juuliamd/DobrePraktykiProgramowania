from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt

from auth_app_exc.users_db import USERS_DB
from auth_app_exc.security import verify_token



app = FastAPI()
SECRET_KEY = "super_secret_key" # w praktyce trzymane w zmiennych środowiskowych
ALGORITHM = "HS256"

# prosty logger
logger = logging.getLogger("auth_app_exc")
logging.basicConfig(level=logging.INFO)

class LoginData(BaseModel):
    username: str
    password: str
    
@app.post("/login")
def login(data: LoginData):
    try:
        username = data.username
        password = data.password.encode('utf-8')

        logger.info(f"Login attempt for user: %s", username)

        # USERS_DB now stores a dict with "password" and "roles"
        if username not in USERS_DB:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_record = USERS_DB[username]
        hashed_pw = user_record.get("password")
        if not hashed_pw or not bcrypt.checkpw(password, hashed_pw):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # include roles in the token so handlers can enforce role-based access
        payload = {
            "sub": username,
            "roles": user_record.get("roles", []),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        # ensure token is a str for JSON serialisation
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        # re-raise known HTTP errors
        raise
    except Exception as exc:
        logger.exception("Unhandled error in /login: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/users")
def create_user(data: LoginData, current_user: dict = Depends(verify_token)):
    try:
        username = data.username
        password = data.password.encode('utf-8')

        logger.info(f"User creation attempt for: %s", username)

        # Only admins may create users
        roles = current_user.get("roles", []) if current_user else []
        if "ROLE_ADMIN" not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

        if username in USERS_DB:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        # store new user with default ROLE_USER
        USERS_DB[username] = {"password": hashed_pw, "roles": ["ROLE_USER"]}
        logger.info(f"User created successfully: %s", username)
        return {"message": "User created successfully"}

    except HTTPException:
        # re-raise known HTTP errors
        raise
    except Exception as exc:
        logger.exception("Unhandled error in /users: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


# Minimalne zabezpieczenie wszystkich endpointów (poza białą listą)
PUBLIC_PATHS = {
    "/login",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/docs/oauth2-redirect"
}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS:
        return await call_next(request)

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Authorization header missing"})

    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid authorization scheme"})

    token = auth.split(" ", 1)[1]
    try:
        # validate token signature and exp using jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload or payload.get("sub") is None:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token payload"})
        # attach payload for handlers
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token has expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token"})
    except Exception:
        logger.exception("Unexpected error in auth middleware")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})

    return await call_next(request)


@app.get("/me")
def get_current_user(current_user: dict = Depends(verify_token)):
    """Small helper endpoint to return the token payload (useful for debugging roles)."""
    # Return the payload as-is so clients can inspect 'roles' and other claims
    return {"current_user": current_user}


@app.get("/user_details")
def user_details(current_user: dict = Depends(verify_token)):
    """Return structured user details extracted from JWT payload.

    Provides `username` (from `sub`) and `roles` for easy client consumption.
    """
    username = current_user.get("sub")
    roles = current_user.get("roles", [])
    return {
        "username": username,
        "roles": roles,
        "payload": current_user,
    }

from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
import logging
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
import bcrypt

from auth_app_exc.users_db import USERS_DB
from auth_app_exc.security import verify_token



app = FastAPI()
SECRET_KEY = "super_secret_key" # w praktyce trzymane w zmiennych środowiskowych
ALGORITHM = "HS256"

# prosty logger
logger = logging.getLogger("auth_app_exc")
logging.basicConfig(level=logging.INFO)

class LoginData(BaseModel):
    username: str
    password: str
    
@app.post("/login")
def login(data: LoginData):
    try:
        username = data.username
        password = data.password.encode('utf-8')

        logger.info(f"Login attempt for user: %s", username)

        # USERS_DB now stores a dict with "password" and "roles"
        if username not in USERS_DB:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_record = USERS_DB[username]
        hashed_pw = user_record.get("password")
        if not hashed_pw or not bcrypt.checkpw(password, hashed_pw):
            raise HTTPException(status_code=401, detail="Invalid credentials")

        # include roles in the token so handlers can enforce role-based access
        payload = {
            "sub": username,
            "roles": user_record.get("roles", []),
            "iat": datetime.utcnow(),
            "exp": datetime.utcnow() + timedelta(hours=1)
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
        # ensure token is a str for JSON serialisation
        if isinstance(token, bytes):
            token = token.decode('utf-8')
        return {"access_token": token, "token_type": "bearer"}

    except HTTPException:
        # re-raise known HTTP errors
        raise
    except Exception as exc:
        logger.exception("Unhandled error in /login: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")
    
@app.post("/users")
def create_user(data: LoginData, current_user: dict = Depends(verify_token)):
    try:
        username = data.username
        password = data.password.encode('utf-8')

        logger.info(f"User creation attempt for: %s", username)

        # Only admins may create users
        roles = current_user.get("roles", []) if current_user else []
        if "ROLE_ADMIN" not in roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin role required")

        if username in USERS_DB:
            raise HTTPException(status_code=400, detail="User already exists")

        hashed_pw = bcrypt.hashpw(password, bcrypt.gensalt())
        # store new user with default ROLE_USER
        USERS_DB[username] = {"password": hashed_pw, "roles": ["ROLE_USER"]}
        logger.info(f"User created successfully: %s", username)
        return {"message": "User created successfully"}

    except HTTPException:
        # re-raise known HTTP errors
        raise
    except Exception as exc:
        logger.exception("Unhandled error in /users: %s", exc)
        raise HTTPException(status_code=500, detail="Internal server error")


# Minimalne zabezpieczenie wszystkich endpointów (poza białą listą)
PUBLIC_PATHS = {
    "/login",
    "/openapi.json",
    "/docs",
    "/redoc",
    "/docs/oauth2-redirect"
}


@app.middleware("http")
async def auth_middleware(request: Request, call_next):
    path = request.url.path
    if path in PUBLIC_PATHS:
        return await call_next(request)

    auth = request.headers.get("authorization") or request.headers.get("Authorization")
    if not auth:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Authorization header missing"})

    if not auth.startswith("Bearer "):
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid authorization scheme"})

    token = auth.split(" ", 1)[1]
    try:
        # validate token signature and exp using jwt
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if not payload or payload.get("sub") is None:
            return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token payload"})
        # attach payload for handlers
        request.state.user = payload
    except jwt.ExpiredSignatureError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Token has expired"})
    except jwt.InvalidTokenError:
        return JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content={"detail": "Invalid token"})
    except Exception:
        logger.exception("Unexpected error in auth middleware")
        return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, content={"detail": "Internal server error"})

    return await call_next(request)


@app.get("/me")
def get_current_user(current_user: dict = Depends(verify_token)):
    """Small helper endpoint to return the token payload (useful for debugging roles)."""
    # Return the payload as-is so clients can inspect 'roles' and other claims
    return {"current_user": current_user}


@app.get("/user_details")
def user_details(current_user: dict = Depends(verify_token)):
    """Return structured user details extracted from JWT payload.

    Provides `username` (from `sub`) and `roles` for easy client consumption.
    """
    username = current_user.get("sub")
    roles = current_user.get("roles", [])
    return {
        "username": username,
        "roles": roles,
        "payload": current_user,
    }