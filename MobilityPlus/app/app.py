import os
# import sqlite3
# import subprocess
# from datetime import datetime, timedelta
# from typing import Optional
# from urllib.request import Request
#
# from google.oauth2 import id_token
# from google.auth.transport import requests
import jwt
from fastapi import Depends, HTTPException, status
from fastapi import FastAPI, WebSocket, Response
# from fastapi.openapi.models import OAuthFlows as OAuthFlowsModel
# from fastapi.responses import RedirectResponse
# from fastapi.security import OAuth2
# from fastapi.security import SecurityScopes
# from fastapi.security.utils import get_authorization_scheme_param
# from passlib.context import CryptContext
# from pydantic import BaseModel

# FastAPI app instance
app = FastAPI()

# Secrets should be stored securely, not hardcoded
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

from fastapi import FastAPI, HTTPException
# from fastapi.responses import RedirectResponse
from google.oauth2 import id_token
from google.auth.transport import requests

# FastAPI app instance
app = FastAPI()

# Secrets should be stored securely, not hardcoded
CLIENT_SECRET = os.getenv('CLIENT_SECRET')

def verify_token(token):
    try:
        # Specify the CLIENT_ID of the app that accesses the backend
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), CLIENT_SECRET)

        if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise ValueError('Wrong issuer.')

        # ID token is valid. Get the user's Google Account ID from the decoded token
        userid = idinfo['sub']
    except ValueError:
        # Invalid token
        raise HTTPException(401, "Invalid token")

    # Rest of your code...

@app.post("/token")
async def login(form_data: str):
    if form_data:
        try:
            # Specify the CLIENT_ID of the app that accesses the backend:
            idinfo = id_token.verify_oauth2_token(form_data, requests.Request(),
                                                  os.getenv('GOOGLE_CLIENT_ID'))

            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')

            # ID token is valid. Get the user's Google Account ID from the decoded token.
            userid = idinfo['sub']
        except ValueError:
            # Invalid token
            raise HTTPException(401, "Invalid token")

        # Authenticate the user
        user = await load_user(userid)
        if not user:
            raise HTTPException(401, "Invalid user")

        response = Response(content='Logged in', status_code=303)
        response.headers["Location"] = "http://localhost:63342/MobilityPlus/app/templates/integrate.html"
        return response



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    token = websocket.query_params.get("token")
    if not token:
        await websocket.send_text("Unauthorized access. Please login.")
        await websocket.close()
        return

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=username)
    except (jwt.JWTError, ValidationError):
        raise credentials_exception
    user = await load_user(token_data.username)
    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": "Bearer"},
            )
    while True:
        data = await websocket.receive_text()
        print(f"Received message: {data}")

        # Rest of your code...

@app.exception_handler(HTTPException)
async def auth_exception_handler(request, exc):
    if exc.status_code == 401:
        return {"detail": exc.detail}, exc.status_code

# Run the application (modify host and port as needed)
if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="localhost", port=8000)
    print("server up and running")
