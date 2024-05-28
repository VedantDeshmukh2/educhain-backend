from fastapi import FastAPI, status, HTTPException
from pydantic import BaseModel
from typing import List
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Connect to the database (example using PostgreSQL)
# DATABASE_URL = os.getenv("DATABASE_URL")

# Define the data model


class Item(BaseModel):
    id: int
    name: str
    description: str


app = FastAPI()

# In-memory database for demonstration purposes
items = [
    {
        "id": 1,
        "name": "Item 1",
        "description": "Description for item 1"
    },
    {
        "id": 2,
        "name": "Item 2",
        "description": "Description for item 2"
    }
]


# Root path
@app.get("/", status_code=status.HTTP_200_OK)
def root():
    return {"message": "Server is running"}


# CRUD operations
@app.get("/items", response_model=List[Item])
def get_items():
    return items


@app.post("/items", response_model=Item)
def create_item(item: Item):
    items.append(item)
    return item


@app.get("/items/{item_id}", response_model=Item)
def get_item(item_id: int):
    for item in items:
        if item.id == item_id:
            return item
    raise HTTPException(status_code=404, detail="Item not found")


@app.put("/items/{item_id}", response_model=Item)
def update_item(item_id: int, updated_item: Item):
    for i, item in enumerate(items):
        if item.id == item_id:
            items[i] = updated_item
            return updated_item
    raise HTTPException(status_code=404, detail="Item not found")


@app.delete("/items/{item_id}")
def delete_item(item_id: int):
    for i, item in enumerate(items):
        if item.id == item_id:
            items.pop(i)
            return {"message": "Item deleted"}
    raise HTTPException(status_code=404, detail="Item not found")
