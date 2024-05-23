from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from final_pipeline import process_text

app = FastAPI()

# Указываем директорию для статических файлов
app.mount("/static", StaticFiles(directory=Path(__file__).parent / "static"), name="static")


# Создаем маршрут для главной страницы
@app.get("/", response_class=HTMLResponse)
async def read_index():
    with open(Path(__file__).parent / "templates" / "index.html") as f:
        return f.read()


# Создаем маршрут для обработки текста
@app.post("/analyze-text/")
async def analyze_text(text: str = Form(...)):
    # Используем функцию для обработки текста
    result_text = process_text(text)
    return {"result_text": result_text}
