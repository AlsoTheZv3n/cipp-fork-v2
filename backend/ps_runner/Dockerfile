FROM mcr.microsoft.com/powershell:7.4-ubuntu-22.04

WORKDIR /app

# Install Exchange Online module ONCE at build time
RUN pwsh -Command "\
    Set-PSRepository PSGallery -InstallationPolicy Trusted; \
    Install-Module ExchangeOnlineManagement -Force -AllowClobber -Scope AllUsers; \
    Install-Module Microsoft.Graph.Authentication -Force -Scope AllUsers"

COPY runner.ps1 .

# Health check
HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD pwsh -Command "try { (Invoke-WebRequest -Uri 'http://localhost:8001/health' -UseBasicParsing).StatusCode -eq 200 } catch { exit 1 }"

EXPOSE 8001

CMD ["pwsh", "-File", "runner.ps1"]
