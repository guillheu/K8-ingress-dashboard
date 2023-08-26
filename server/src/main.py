from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import threading

from config import all_configs as CONFIG
from watchers import watch_ingresses, watch_ingress_classes

app = FastAPI()


# Static files directory
app.mount("/static", StaticFiles(directory=CONFIG.get('HTML_DIR')), name="static")

# Serve the static index.html page
@app.get("/")
def root():
    return FileResponse(f"{CONFIG.get('HTML_DIR')}/index.html")

# Serve the favicon
@app.get("/favicon.ico")
def root():
    return FileResponse(f"{CONFIG.get('HTML_DIR')}/favicon.ico")

# Serve the static ingresses.json file
@app.get("/ingresses")
def ingresses():
    return FileResponse(f"{CONFIG.get('HTML_DIR')}/ingresses.json")


# Function to run on startup
@app.on_event("startup")
async def startup_event():
    threading.Thread(target=watch_ingresses, daemon=True).start()
    threading.Thread(target=watch_ingress_classes, daemon=True).start()