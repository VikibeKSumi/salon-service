from fastapi import Request, Header, HTTPException

def get_current_user(request: Request, authorization: str = Header(None)) -> str:
    session_id = (authorization or "").removeprefix("Bearer ")
    email = request.app.state.redis.get(f"session_id:{session_id}")
    if not email:
        raise HTTPException(status_code=401, detail="not logged in")
    return email
