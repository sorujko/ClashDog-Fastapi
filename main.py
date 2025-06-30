from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from routers import root, fighters, tournaments

app = FastAPI()

app.mount("/images", StaticFiles(directory="images"), name="images")
# Set up Jinja2 templates (make sure your templates are in 'templates' folder)
templates = Jinja2Templates(directory="templates")

app.include_router(root.router)
app.include_router(fighters.router)
app.include_router(tournaments.router)