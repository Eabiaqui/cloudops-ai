"""Entry point: python -m cloudops_ai"""

import uvicorn
from cloudops_ai.config import settings

if __name__ == "__main__":
    uvicorn.run(
        "cloudops_ai.api:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=False,  # managed by systemd; use watchfiles in dev via uvicorn CLI
    )
