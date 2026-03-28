from fastapi import FastAPI, Query, Response, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
import math

app = FastAPI()

# ---------------------- DATA ----------------------

books = [
    {"id": 1, "title": "Python Basics", "author": "John", "genre": "Tech", "is_available": True},
    {"id": 2, "title": "AI Future", "author": "Alice", "genre": "Science", "is_available": True},
    {"id": 3, "title": "History of India", "author": "Raj", "genre": "History", "is_available": True},
    {"id": 4, "title": "Fiction World", "author": "Sam", "genre": "Fiction", "is_available": False},
    {"id": 5, "title": "Data Science", "author": "Mike", "genre": "Tech", "is_available": True},
    {"id": 6, "title": "Space Science", "author": "Neil", "genre": "Science", "is_available": True},
]

borrow_records = []
record_counter = 1
queue = []

# ---------------------- HELPERS ----------------------

def find_book(book_id):
    for book in books:
        if book["id"] == book_id:
            return book
    return None

def calculate_due_date(days, member_type):
    base_day = 15
    
    if member_type == "premium":
        return f"Return by: Day {base_day + min(days, 60)}"
    return f"Return by: Day {base_day + min(days, 30)}"

# ---------------------- MODELS ----------------------

class BorrowRequest(BaseModel):
    member_name: str = Field(..., min_length=2)
    book_id: int = Field(..., gt=0)
    borrow_days: int = Field(..., gt=0, le=30)
    member_id: str = Field(..., min_length=4)
    member_type: str = "regular"

class NewBook(BaseModel):
    title: str = Field(..., min_length=2)
    author: str = Field(..., min_length=2)
    genre: str = Field(..., min_length=2)
    is_available: bool = True

# ---------------------- FIXED ROUTES (Must be ABOVE /{id}) ----------------------

@app.get("/")
def home():
    return {"message": "Welcome to City Public Library"}

@app.get("/books/summary")
def books_summary():
    genre_count = {}
    for b in books:
        genre_count[b["genre"]] = genre_count.get(b["genre"], 0) + 1
    return {
        "total": len(books),
        "available": len([b for b in books if b["is_available"]]),
        "borrowed": len([b for b in books if not b["is_available"]]),
        "genre_breakdown": genre_count
    }

@app.get("/books/filter")
def filter_books(
    genre: Optional[str] = None, 
    author: Optional[str] = None, 
    is_available: Optional[bool] = None
):
    result = books

    if genre is not None: 
        result = [b for b in result if b["genre"].lower() == genre.lower()]
    if author is not None: 
        result = [b for b in result if b["author"].lower() == author.lower()]
    if is_available is not None: 
        result = [b for b in result if b["is_available"] == is_available]
    return {"count": len(result), "books": result}

@app.get("/books/search")
def search_books(keyword: str):
    result = [b for b in books if keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()]
    if not result:
        return {"message": f"No books found for '{keyword}'. Try another search!", "total_found": 0, "books": []}
    return {"total_found": len(result), "books": result}

@app.get("/books/sort")
def sort_books(sort_by: str = "title", order: str = "asc"):
    if sort_by not in ["title", "author", "genre"]:
        return {"error": "Invalid sort_by. Use title, author, or genre"}
    if order not in ["asc", "desc"]:
        return {"error": "Invalid order. Use asc or desc"}
    
    sorted_books = sorted(books, key=lambda x: x[sort_by], reverse=(order == "desc"))
    return {"sorted_by": sort_by, "order": order, "books": sorted_books}

@app.get("/books/page")
def paginate_books(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):

    start = (page - 1) * limit
    total_pages = math.ceil(len(books) / limit)
    return {
        "total": len(books),
        "total_pages": total_pages,
        "page": page,
        "limit": limit,
        "books": books[start:start + limit]
    }

@app.get("/borrow-records/search")
def search_records(member_name: str):
    result = [r for r in borrow_records if member_name.lower() in r["member_name"].lower()]
    return {"count": len(result), "records": result}

@app.get("/borrow-records/page")
def paginate_records(page: int = Query(1, ge=1), limit: int = Query(3, ge=1, le=10)):
    start = (page - 1) * limit
    total_pages = math.ceil(len(borrow_records) / limit)
    return {"page": page, "total_pages": total_pages, "records": borrow_records[start:start + limit]}

@app.get("/books/browse")
def browse_books(
    keyword: Optional[str] = None, 
    sort_by: str = "title", 
    order: str = "asc", 
    page: int = 1, 
    limit: int = 3
):
    result = books
    if keyword:
        result = [b for b in result if keyword.lower() in b["title"].lower() or keyword.lower() in b["author"].lower()]
    
    if sort_by not in ["title", "author", "genre"]:
        return {"error": "Invalid sort_by"}
        
    result = sorted(result, key=lambda x: x[sort_by], reverse=(order == "desc"))
    start = (page - 1) * limit
    total_pages = math.ceil(len(result) / limit)
    
    return {
        "keyword_used": keyword,
        "sort_settings": f"{sort_by} {order}",
        "total": len(result),
        "total_pages": total_pages,
        "books": result[start:start + limit]
    }

@app.get("/books")
def get_books():
    return {"total": len(books), "available_count": len([b for b in books if b["is_available"]]), "books": books}

@app.get("/borrow-records")
def get_records():
    return {"total": len(borrow_records), "records": borrow_records}

@app.get("/queue")
def get_queue():
    return {"queue": queue}

# ---------------------- VARIABLE ROUTES (Must be BELOW fixed) ----------------------

@app.get("/books/{book_id}")
def get_book(book_id: int):
    book = find_book(book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    return book

# ---------------------- POST / PUT / DELETE ----------------------

@app.post("/borrow")
def borrow_book(data: BorrowRequest):
    global record_counter
    book = find_book(data.book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    if not book["is_available"]: return {"error": "Book already borrowed"}

    book["is_available"] = False
    record = {
        "record_id": record_counter, 
        "member_name": data.member_name, 
        "book_id": data.book_id, 
        "due_date": calculate_due_date(data.borrow_days, data.member_type)
    }
    borrow_records.append(record)
    record_counter += 1
    return record

@app.post("/books")
def add_book(data: NewBook, response: Response):
    if any(b["title"].lower() == data.title.lower() for b in books):
        return {"error": "Duplicate book title exists"}
    new_book = {"id": len(books) + 1, **data.dict()}
    books.append(new_book)
    response.status_code = 201
    return new_book

@app.put("/books/{book_id}")
def update_book(book_id: int, genre: Optional[str] = None, is_available: Optional[bool] = None):
    book = find_book(book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    if genre is not None: book["genre"] = genre
    if is_available is not None: book["is_available"] = is_available
    return book

@app.delete("/books/{book_id}")
def delete_book(book_id: int):
    book = find_book(book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    
 
    if not book["is_available"]:
        return {"error": "Cannot delete a book that is currently borrowed."}
        
    books.remove(book)
    return {"message": f"'{book['title']}' has been deleted from the system."}

@app.post("/queue/add")
def add_to_queue(member_name: str, book_id: int):
    book = find_book(book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    if book["is_available"]: return {"error": "Book is available, no need to queue"}
    queue.append({"member_name": member_name, "book_id": book_id})
    return {"message": "Added to queue", "queue": queue}

@app.post("/return/{book_id}")
def return_book(book_id: int):
    global record_counter
    book = find_book(book_id)
    if not book: raise HTTPException(status_code=404, detail="Book not found")
    
    book["is_available"] = True
    for q in queue:
        if q["book_id"] == book_id:
            queue.remove(q)
            book["is_available"] = False
        
            record = {"record_id": record_counter, "member_name": q["member_name"], "book_id": book_id, "due_date": calculate_due_date(7, "regular")}
            borrow_records.append(record)
            record_counter += 1
            return {"message": "Returned and auto-assigned to next person in queue", "record": record}
    return {"message": "Returned and now available"}
