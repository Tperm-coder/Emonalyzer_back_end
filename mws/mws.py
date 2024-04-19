from fastapi import FastAPI, Request, FastAPI, HTTPException, status
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from app.mws.token_authorization import authenticate_token


def inject_middlewares(app):

    @app.middleware("http")
    async def auth_mw(request: Request, call_next):

        # workaround for now
        url_path = request.url.path
        print(url_path)
        if "register" in url_path or "login" in url_path or "docs" in url_path or "openapi" in url_path or "upload_audio" in url_path:
            response = await call_next(request)
            return response


        headers = dict(request.headers)
        token = headers["token"]

        mw_res = authenticate_token(token=token,required_fields=["name","id"])

        if mw_res["state"] == False:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )


        request.state.token = mw_res["data"]
   
        response = await call_next(request)
        return response