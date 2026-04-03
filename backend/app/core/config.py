from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Database
    database_url: str = "postgresql+asyncpg://cipp:changeme@localhost:5433/cipp"

    # Azure AD — Partner Tenant (for GDAP Graph API calls)
    azure_tenant_id: str = ""
    azure_client_id: str = ""
    azure_client_secret: str = ""

    # Azure AD — CIPP App Auth (for user login to dashboard)
    auth_tenant_id: str = ""  # Same as azure_tenant_id if single-tenant
    auth_client_id: str = ""  # App Registration for CIPP UI
    auth_client_secret: str = ""
    auth_redirect_uri: str = "http://localhost:8055/.auth/callback"
    jwt_secret: str = "change-me-in-production"
    session_expiry_hours: int = 24

    # PowerShell Runner
    ps_runner_url: str = "http://localhost:8001"

    # App
    app_name: str = "CIPP Backend"
    debug: bool = False
    demo_mode: bool = False  # Set to true for fake data without Azure credentials
    cors_origins: list[str] = ["http://localhost:3000"]
    frontend_url: str = "http://localhost:3000"

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
