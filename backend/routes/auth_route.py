from fastapi import APIRouter, Request, HTTPException, Header
import bcrypt, secrets
from schemas.auth_schema import LoginInput


auth_router = APIRouter()
 

@auth_router.post('/login')
def login(body: LoginInput, request: Request):
   
    email, password = body.email,  body.password

    with request.app.state.pool.connection() as conn:
        row = conn.execute("""
            SELECT password_hash FROM owners WHERE email = %s
        """,
        (email,)
        ).fetchone()

    hashed_password = row[0] if row else None
    if not hashed_password or not bcrypt.checkpw(password.encode(), hashed_password.encode()):
        raise HTTPException(
            status_code=401,
            detail="wrong email or password"
        )

    session_id = secrets.token_hex(16)
    request.app.state.redis.set(name=f"session_id:{session_id}", value=email, nx=True, ex=request.app.state.session_ttl)
    return {"session_id": session_id}


@auth_router.post("/logout")
def logout(request: Request, authorization: str = Header(None)):
    session_id = (authorization or "").removeprefix("Bearer ")
    request.app.state.redis.delete(f"session_id:{session_id}")
    return {"ok": True}
