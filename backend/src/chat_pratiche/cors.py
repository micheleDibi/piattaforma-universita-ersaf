"""Le origini Universo non ottengono accesso alle API autenticate con cookie."""
from starlette.middleware.cors import CORSMiddleware

from src.config import get_impostazioni
from src.chat_pratiche.configurazione import configurazione


class CorsApplicazioni:
    def __init__(self, app):
        self.app = CORSMiddleware(app, allow_origins=get_impostazioni().lista_cors_origins,
            allow_credentials=True, allow_methods=["*"], allow_headers=["*"],
            expose_headers=["Retry-After"])
        self.universo = CORSMiddleware(app,
            allow_origins=[x.strip() for x in configurazione().chat_universo_origini.split(",") if x.strip()],
            allow_credentials=False, allow_methods=["GET", "POST"],
            allow_headers=["Authorization", "Content-Type"])

    async def __call__(self, scope, receive, send):
        handler = self.universo if scope.get("path", "").startswith("/realtime/") else self.app
        await handler(scope, receive, send)
