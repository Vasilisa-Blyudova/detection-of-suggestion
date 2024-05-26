from pathlib import Path
from fastapi import FastAPI, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from assets.highlight import process_text, get_score, get_result

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")
templates = Jinja2Templates(directory=Path(__file__).parent / "templates")


def generate_icons(binary_list):
    icons = []
    for value in binary_list:
        if value == 1:
            icons.append("✔️")
        else:
            icons.append("❌")
    return icons


@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    icons = []
    return templates.TemplateResponse("index.html", {"request": request, "icons": icons})


@app.post("/analyze-text/")
async def analyze_text(text: str = Form(...)):
    binary_list = [1, 0, 1, 0, 1, 0, 1, 0, 1, 0]
    icons = generate_icons(binary_list)
    result_text = process_text(text)
    score = get_score()
    result = get_result()
    return {"result_text": result_text, "icons": icons, "score": score, "result": result}
