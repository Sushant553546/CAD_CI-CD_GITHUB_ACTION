from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import json
import os

app = FastAPI(title="Library Management API")
DATA_FILE = "books.json"

# --- Models ---
class Book(BaseModel):
    id: int
    title: str
    author: str
    status: str = "available" # 'available' or 'borrowed'

# --- Helper Functions ---
def load_books():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_books(books):
    with open(DATA_FILE, "w") as f:
        json.dump(books, f, indent=4)

# --- API Endpoints ---
@app.get("/") 
def home(): return { "message":"Code modified for CI/CD deployment!" }

@app.get("/", tags=["Root"])
def read_root():
    return {"message": "Welcome to the Library Management API"}

@app.get("/books", response_model=list[Book], tags=["Books"])
def get_all_books():
    """Retrieve a list of all books in the library."""
    return load_books()

@app.get("/books/{book_id}", response_model=Book, tags=["Books"])
def get_book(book_id: int):
    """Retrieve a specific book by its ID."""
    books = load_books()
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

@app.post("/books", response_model=Book, tags=["Books"])
def add_book(book: Book):
    """Add a new book to the library."""
    books = load_books()
    if any(b["id"] == book.id for b in books):
        raise HTTPException(status_code=400, detail="Book with this ID already exists")
    
    books.append(book.model_dump())
    save_books(books)
    return book

@app.put("/books/{book_id}", response_model=Book, tags=["Books"])
def update_book(book_id: int, updated_book: Book):
    """Update a book's details (e.g., checking it out or returning it)."""
    books = load_books()
    for i, book in enumerate(books):
        if book["id"] == book_id:
            # Ensure the ID in the payload matches the URL
            if updated_book.id != book_id:
                raise HTTPException(status_code=400, detail="ID in URL and body must match")
            
            books[i] = updated_book.model_dump()
            save_books(books)
            return updated_book
    raise HTTPException(status_code=404, detail="Book not found")

@app.delete("/books/{book_id}", tags=["Books"])
def delete_book(book_id: int):
    """Remove a book from the library database."""
    books = load_books()
    for i, book in enumerate(books):
        if book["id"] == book_id:
            del books[i]
            save_books(books)
            return {"message": f"Book with ID {book_id} deleted successfully"}
    raise HTTPException(status_code=404, detail="Book not found")