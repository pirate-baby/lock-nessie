import click
import uvicorn
from datetime import datetime
from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse, HTMLResponse
from common.logger import get_logger
from server.main import router

app = FastAPI(title="Lock-Nessie Auth Server", version="0.0.1")
app.include_router(router)

logger = get_logger(__name__)

@app.get("/")
def home(request: Request):
    """Home page"""
    user = request.cookies.get("user", None)
    expires = request.cookies.get("openid_expires", None)
    if not (user and expires):
        logger.info("No user found, redirecting to login")
        return RedirectResponse(url="/auth/login")
    expires = datetime.fromtimestamp(int(expires))
    logger.info(f"User {user} found, returning home page")
    return HTMLResponse(content=f"Hello {user}. Your login requires a refresh at {expires}.")


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