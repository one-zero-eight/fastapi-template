from src.app.users import router as router_users
from src.app.auth import router as router_auth

routers = [router_users, router_auth]

__all__ = ["routers"]
