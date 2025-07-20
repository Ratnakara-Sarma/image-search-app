from fastapi import FastAPI
from fastapi import Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from query import ChromaDB
from explainer import explain_relevance
from contextlib import asynccontextmanager


@asynccontextmanager
async def lifespan(app: FastAPI):
    ''' Run at startup
        Initialize the Client and add it to app.state
    '''
    app.state.db_client = ChromaDB()
    app.state.explainer = explain_relevance()
    yield

IMAGES_BASE_PATH = r"images"

app = FastAPI(
    title="image-search-backend",
    swagger_ui_parameters={"defaultModelsExpandDepth": -1},
    lifespan=lifespan
)

app.mount("/static", StaticFiles(directory=IMAGES_BASE_PATH), name="static")
templates = Jinja2Templates(directory="templates")
templates.env.filters['zip'] = zip
templates.env


def explain_relevant_images(request:Request, query, metadatas):
    explanation_list = []

    for metadata in metadatas:
        caption = metadata.get("caption")
        explanation = request.app.state.explainer.generate_explanation(query=query,
                                                                       caption=caption)
        explanation_list.append(explanation)
    return explanation_list


@app.get("/", response_class=HTMLResponse)
async def main(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/search")
async def semantic_search(request:Request, query:str=None) -> list:
    db_connection = request.app.state.db_client
    results = db_connection.query_collection(query=query, n_results=5)
    relevant_images = results["ids"][0]
    image_list = [f"static/{img}" for img in relevant_images]

    explanation_list = explain_relevant_images(request=request, query=query,
                                         metadatas=results['metadatas'][0])
    return templates.TemplateResponse("index.html", {
        "request": request,
        "image_list": image_list,
        "explanation_list": explanation_list
    })