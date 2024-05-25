from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from assets.highlight import process_text

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def generate_icons(binary_list):
    icons = []
    for value in binary_list:
        if value == 1:
            icons.append("✔️")  # Green checkmark
        else:
            icons.append("❌")  # Red cross
    return icons


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    binary_list = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]  # Example list
    icons = generate_icons(binary_list)
    return templates.TemplateResponse("index.html", {"request": request, "icons": icons})


@app.post("/analyze-text/")
async def analyze_text(text: str = Form(...)):
    result_text = process_text(text)
    return {"result_text": result_text}
