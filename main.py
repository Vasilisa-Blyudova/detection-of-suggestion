from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from assets.highlight import process_text

app = FastAPI()

app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(Path(__file__).parent / "templates" / "index.html") as f:
        return f.read()


@app.post("/analyze-text/")
async def analyze_text(text: str = Form(...)):
    result_text = process_text(text)
    return {"result_text": result_text}
