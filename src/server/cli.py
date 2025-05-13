import click
import uvicorn
from typing import Optional
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pathlib import Path
import humanize
from common.logger import get_logger
from server.main import router

app = FastAPI(title="Lock-Nessie Auth Server", version="0.0.1")
app.include_router(router)

# Get the directory containing the current file
current_dir = Path(__file__).parent
templates = Jinja2Templates(directory=str(current_dir / "templates"))

# Mount static files
app.mount("/static", StaticFiles(directory=str(current_dir / "static")), name="static")

logger = get_logger(__name__)

@app.get("/")
def home(request: Request,
         aws_secret_arn: Optional[str] = None):
    """Home page"""
    user = request.cookies.get("user", None)
    expires = request.cookies.get("openid_expires", None)
    is_logged_in = bool(user and expires)

    if is_logged_in:
        expires_dt = datetime.fromtimestamp(int(expires))
        now = datetime.now()
        time_until_expiry = humanize.naturaldelta(expires_dt - now)
        logger.info(f"User {user} found, returning home page")
    else:
        logger.info("No user found, showing login page")
        user = None
        expires_dt = None
        time_until_expiry = None

    return templates.TemplateResponse(
        "home.html",
        {
            "request": request,
            "user": user,
            "is_logged_in": is_logged_in,
            "expires": expires_dt,
            "time_until_expiry": time_until_expiry,
            "aws_secret_arn": aws_secret_arn
        }
    )


@click.group()
def cli():
    """Lock-Nessie CLI tool"""
    pass

@cli.command()
@click.option("--host", default="0.0.0.0", help="Host to bind the server to")
@click.option("--port", default=8000, help="Port to bind the server to")
@click.option("--reload", is_flag=True, help="Enable auto-reload on code changes")
def server(host: str, port: int, reload: bool):
    """Start the Lock-Nessie authentication server"""
    uvicorn.run(
        "server.cli:app",
        host=host,
        port=port,
        reload=reload,
    )

if __name__ == "__main__":
    cli()