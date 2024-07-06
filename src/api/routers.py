from src.modules.user.router import router as router_users
from src.modules.auth.router import router as router_auth

routers = [router_users, router_auth]

__all__ = ["routers"]
