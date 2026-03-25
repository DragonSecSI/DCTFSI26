import os
from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import mydown
import uvicorn

app = FastAPI(title="mydown Renderer")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    """Serve the static index.html page with the editor and preview pane."""
    return HTMLResponse(content=open("static/index.html").read(), status_code=200)


@app.post("/render", response_class=HTMLResponse)
async def render_mydown(mydown_text: str = Form(...)):
    """Convert mydown text to HTML and return it."""
    html_content = mydown.render_mydown(mydown_text)
    return html_content

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=int(os.getenv("PORT", default="8000")), reload=True)
