"""Simple async logger that writes to the cipp_logs PostgreSQL table."""
from app.core.database import async_session


async def log_error(message: str, tenant_id: str = None, source: str = None, data: dict = None):
    """Log an error to the cipp_logs table. Non-blocking, fire-and-forget."""
    try:
        from app.models.template import CippLog
        async with async_session() as session:
            log = CippLog(level="error", message=message[:500], tenant_id=tenant_id, source=source, data=data)
            session.add(log)
            await session.commit()
    except Exception:
        pass  # Don't let logging errors crash the app


async def log_warning(message: str, tenant_id: str = None, source: str = None):
    """Log a warning."""
    try:
        from app.models.template import CippLog
        async with async_session() as session:
            log = CippLog(level="warning", message=message[:500], tenant_id=tenant_id, source=source)
            session.add(log)
            await session.commit()
    except Exception:
        pass


async def log_info(message: str, tenant_id: str = None, source: str = None):
    """Log an info message."""
    try:
        from app.models.template import CippLog
        async with async_session() as session:
            log = CippLog(level="info", message=message[:500], tenant_id=tenant_id, source=source)
            session.add(log)
            await session.commit()
    except Exception:
        pass
