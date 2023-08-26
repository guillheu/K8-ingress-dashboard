from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import threading

from config import all_configs as CONFIG
from watchers import watch_ingresses, watch_ingress_classes

app = FastAPI()


# Static files directory
app.mount("/", StaticFiles(directory=CONFIG.get('HTML_DIR')), name="static")

# Function to run on startup
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=watch_ingresses, daemon=True).start()
    threading.Thread(target=watch_ingress_classes, daemon=True).start()