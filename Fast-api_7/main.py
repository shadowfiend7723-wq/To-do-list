from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from pymongo import MongoClient
from fastapi import Form
from pydantic import BaseModel
from typing import Optional


app = FastAPI()
templates = Jinja2Templates(directory="templates")
client = MongoClient("mongodb://localhost:27017/")
db = client["Nextdb"]
collection = db["Todos"]


class Item(BaseModel):
    id: Optional[int] = None
    task: str
    description: Optional[str] = None
    is_completed: bool = False


@app.get("/", response_class=HTMLResponse)
def read_todos(request: Request):
    # return all todos; show newest first
    todos = list(collection.find().sort("id", -1))
    return templates.TemplateResponse("index.html", {"request": request, "todos": todos})


@app.post("/add")
def add_todo(
    request: Request,
    task: str = Form(...),
    description: Optional[str] = Form(None),
    is_completed: Optional[str] = Form(None),
):
    # auto-generate integer id by taking the current max id and adding 1
    last = collection.find_one(sort=[("id", -1)])
    next_id = (last["id"] + 1) if last and isinstance(last.get("id"), int) else 1

    todo = Item(id=next_id, task=task, description=description, is_completed=bool(is_completed))
    collection.insert_one(todo.dict())
    return RedirectResponse("/", status_code=303)


@app.post("/delete/{id}")
def delete_todo(id: int):
    collection.delete_one({"id": id})
    return RedirectResponse("/", status_code=303)

    