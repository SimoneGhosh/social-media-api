from typing import Optional
from fastapi import FastAPI, Body, Response, status, HTTPException, Depends
from pydantic import BaseModel
from random import randrange
import time

import psycopg2
from psycopg2.extras import RealDictCursor

from . import models, schemas
from .database import engine, SessionLocal

from sqlalchemy.orm import Session

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Connect to Database
while True:
    try:
        conn = psycopg2.connect(host='localhost', database='socialmediaapi', user='postgres',
                                password='Generis2026', cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connecton was successfull")
        break
    except Exception as error: 
        print("Database connection failed")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"title": "title of post 1", "content": "content of post 1", "id": 1},
            {"title": "favorite foods", "content": "I like pizza", "id": 2}]

# PATH OPERATION
@app.get("/")
def root():
    return {"message": "hi"}

@app.get("/sqlalchemy")
def test_posts(db: Session = Depends(get_db)):

    posts = db.query(models.Post).all()
    print(posts)
    return posts

@app.get("/posts")
def get_posts(db: Session = Depends(get_db)):
    # cursor.execute(""" SELECT * FROM posts """)
    # posts = cursor.fetchall()

    posts = db.query(models.Post).all()
    return posts    

@app.post("/posts", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.PostCreate, db: Session = Depends(get_db)):
    """
    cursor.execute("" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING *"", 
                   (post.title, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    """
    new_post = models.Post(**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return new_post
# title str, content str

@app.get("/posts/{id}")
def get_post(id: int, db: Session = Depends(get_db)):

    #cursor.execute(""" SELECT * FROM posts where id=%s """, (str(id),))
    #post = cursor.fetchone()

    post = db.query(models.Post).filter(models.Post.id == id).first()

    if not post:

        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} was not found")

        """response.status_code = status.HTTP_404_NOT_FOUND
        return {"message": f"post with id: {id} was not found"}"""

    return post

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db)):
    
    #cursor.execute(""" DELETE FROM posts where id=%s RETURNING * """, (str(id),))
    #deleted_post = cursor.fetchone()
    #conn.commit()

    post = db.query(models.Post).filter(models.Post.id == id)

    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post.delete(synchronize_session=False)
    db.commit()

    return Response(status_code=status.HTTP_204_NO_CONTENT)

@app.put("/posts/{id}")
def update_post(id: int, updated_post: schemas.PostCreate, db: Session = Depends(get_db)):

    """cursor.execute("" UPDATE posts SET title=%s, content=%s, published=%s WHERE id=%s RETURNING * "",
                   (post.title, post.content, post.published, str(id)))
    
    updated_post = cursor.fetchone()
    conn.commit()"""

    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()

    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"post with id: {id} does not exist")
    
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()