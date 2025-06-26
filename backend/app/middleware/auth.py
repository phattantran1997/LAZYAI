from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from app.auth.jwt_handler import verify_access_token

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        
        unprotected = [
            "/users/login",
            "/users/register",
            "/auth/refresh",
            "/health"
        ]
        # Allow all OPTIONS requests (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Allow unprotected paths
        if any(request.url.path.startswith(path) for path in unprotected):
            return await call_next(request)
        
        # -------------------------- Check header ---------------------------->
        
        auth_header = request.headers.get("authorization")

        token = None
        if auth_header and " " in auth_header:
            token = auth_header.split(" ", 1)[1]

        # -------------------------- Check cookie ----------------------------->

        # # Check for access_token in cookies
        # token = request.cookies.get("access_token")

        # -------------------------------------------------------------------->

        if not token:
            return JSONResponse(status_code=401, content={"detail": "Not authenticated"})
        try:
            verify_access_token(token)
        except Exception as e:
            return JSONResponse(status_code=401, content={"detail": str(e)})
        
        return await call_next(request)