import uvicorn

from config.settings import APP_HOST, APP_PORT
from container.container import create_app

app = create_app()

if __name__ == "__main__":
    uvicorn.run("main:app", host=APP_HOST, port=APP_PORT, reload=True)
