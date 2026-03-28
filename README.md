
#  Library Book System

##  Project Overview
The **Library Book System** is a backend application built using **FastAPI** designed to manage book inventories, handle borrowing transactions, and track member activity.

This project demonstrates core backend engineering concepts, including:
- RESTful API design
- Pydantic data validation
- CRUD operations
- Multi-step workflows (queue & auto-assignment)
- Search, sorting, and pagination

---

##  Technologies Used

| Technology | Purpose |
| :--- | :--- |
| **Python** | Core programming language |
| **FastAPI** | Backend API framework |
| **Pydantic** | Data validation |
| **Uvicorn** | ASGI server |
| **Swagger UI** | API testing |

---

##  Project Architecture & Features

### 🔹 Route Optimization
All fixed routes (`/books/search`, `/books/filter`, etc.) are placed above variable routes (`/books/{book_id}`) to ensure correct request handling.

---

### 🔹 Multi-Step Workflow
Borrow → Queue → Return → Auto-Assign

- Borrow book → becomes unavailable  
- Users join queue  
- On return → automatically assigned to next user  

---

### 🔹 Advanced Features
-  Search (title + author, case-insensitive)
-  Sorting (title, author, genre)
-  Pagination (page, limit)
-  Combined `/browse` endpoint  

---

## 📂 Project Structure

```

library-book-system/
│
├── main.py
├── requirements.txt
├── README.md
└── screenshots/

````

---

## Installation & Setup

### 1. Create Virtual Environment
```bash
python -m venv venv
````

### 2. Activate Environment

**Windows**

```bash
venv\Scripts\activate
```

**Mac/Linux**

```bash
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

---

### 4. Run Server

```bash
uvicorn main:app --reload
```

---

### 5. Open Swagger

```
http://127.0.0.1:8000/docs
```

---

##  API Summary

###  Basic

* GET `/`
* GET `/books`
* GET `/books/{book_id}`
* GET `/books/summary`

---

###  Discovery

* GET `/books/search`
* GET `/books/sort`
* GET `/books/page`
* GET `/books/browse`

---

###  Workflow

* POST `/borrow`
* POST `/queue/add`
* POST `/return/{book_id}`

---

###  CRUD

* POST `/books`
* PUT `/books/{book_id}`
* DELETE `/books/{book_id}`

---

##  Screenshots

All endpoints (Q1–Q20) are tested.

Located in:

```
/screenshots
```

Includes:

* Success responses
* Error handling
* Validation cases

---

##  Testing

Swagger UI:

```
http://127.0.0.1:8000/docs
```

---

##  Acknowledgement

Developed as part of the **FastAPI Internship at Innomatics Research Labs**.



⭐ Thank you for reviewing this project!

