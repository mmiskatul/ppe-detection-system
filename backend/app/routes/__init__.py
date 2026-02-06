from app.routes.auth import router as auth_router
from app.routes.users import router as users_router
from app.routes.analytics import router as analytics_router
from app.routes.detect import router as detect_router

__all__ = ["auth_router", "users_router", "analytics_router", "detect_router"]
