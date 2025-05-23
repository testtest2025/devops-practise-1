import os
import logging
import sqlalchemy

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy import Column, Integer, String, Float, create_engine
from sqlalchemy.orm import sessionmaker, Session

DATABASE_URL    = os.environ.get("DATABASE_URL", "sqlite:///./books.db")
LOG_LEVEL       = os.environ.get("LOG_LEVEL", "INFO").upper()
PAGE_SIZE       = int(os.environ.get("PAGE_SIZE", "10"))
APP_ENV         = os.environ.get("APP_ENV", "dev")
HOST            = os.environ.get("HOST", "0.0.0.0")
PORT            = int(os.environ.get("PORT", "8080"))
RELOAD          = os.environ.get("RELOAD", "False").lower() == "true"
ALLOWED_ORIGINS = os.environ.get("ALLOWED_ORIGINS", "*").split(",")
DB_POOL_SIZE    = int(os.environ.get("DB_POOL_SIZE", "5"))
DB_MAX_OVERFLOW = int(os.environ.get("DB_MAX_OVERFLOW", "10"))
LOG_FORMAT      = os.environ.get("LOG_FORMAT", "%(levelname)s:%(name)s:%(message)s")


logging.basicConfig(
    level=getattr(logging, LOG_LEVEL, logging.INFO),
    format=LOG_FORMAT
)
logger = logging.getLogger(__name__)


engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {},
    pool_size=DB_POOL_SIZE,
    max_overflow=DB_MAX_OVERFLOW
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = sqlalchemy.orm.declarative_base()

class BookModel(Base):
    __tablename__ = "books"
    id          = Column(Integer, primary_key=True, index=True)
    title       = Column(String, index=True)
    author      = Column(String, index=True)
    description = Column(String, nullable=True)
    price       = Column(Float)


class Book(BaseModel):
    id: int
    title: str
    author: str
    description: Optional[str] = None
    price: float

    class Config:
        from_attributes = True

class BookCreate(BaseModel):
    title: str
    author: str
    description: Optional[str] = None
    price: float

class BookUpdate(BaseModel):
    title: Optional[str] = None
    author: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = None


app = FastAPI(
    title="Books API",
    description=f"Books service ({APP_ENV} environment)",
    version="1.0.0"
)

if ALLOWED_ORIGINS and ALLOWED_ORIGINS != ["*"]:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )


Base.metadata.create_all(bind=engine)
logger.info("Database tables created or verified")


def get_db():
    logger.info("Opening database session")
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
        logger.info("Database session closed")


@app.post("/books/", response_model=Book)
def create_book(book: BookCreate, db: Session = Depends(get_db)):
    logger.info(f"Creating book with data: {book.dict()}")
    db_book = BookModel(**book.dict())
    db.add(db_book)
    db.commit()
    db.refresh(db_book)
    logger.info(f"Created book with ID: {db_book.id}")
    return db_book

@app.get("/books/", response_model=List[Book])
def get_books(page: int = 1, db: Session = Depends(get_db)):
    logger.info(f"Fetching page {page} (size={PAGE_SIZE})")
    offset = (page - 1) * PAGE_SIZE
    books = db.query(BookModel).offset(offset).limit(PAGE_SIZE).all()
    return books

@app.get("/books/{book_id}", response_model=Book)
def get_book(book_id: int, db: Session = Depends(get_db)):
    logger.info(f"Fetching book with ID: {book_id}")
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        logger.warning(f"Book not found: ID {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    return db_book

@app.put("/books/{book_id}", response_model=Book)
def update_book(book_id: int, book_update: BookUpdate, db: Session = Depends(get_db)):
    logger.info(f"Updating book ID {book_id} with data: {book_update.dict(exclude_unset=True)}")
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        logger.warning(f"Book not found for update: ID {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    for key, value in book_update.dict(exclude_unset=True).items():
        setattr(db_book, key, value)
    db.commit()
    db.refresh(db_book)
    return db_book

@app.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, db: Session = Depends(get_db)):
    logger.info(f"Deleting book with ID: {book_id}")
    db_book = db.query(BookModel).filter(BookModel.id == book_id).first()
    if not db_book:
        logger.warning(f"Book not found for deletion: ID {book_id}")
        raise HTTPException(status_code=404, detail="Book not found")
    db.delete(db_book)
    db.commit()
    logger.info(f"Deleted book with ID: {book_id}")
    return {"ok": True}


if __name__ == "__main__":
    logger.info(f"Running Uvicorn server on {HOST}:{PORT}, reload={RELOAD}")
    import uvicorn
    uvicorn.run("main:app", host=HOST, port=PORT, reload=RELOAD)
