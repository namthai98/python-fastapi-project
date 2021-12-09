from typing import Optional
from fastapi import FastAPI, Response, HTTPException, status
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange
import psycopg2
from psycopg2.extras import RealDictCursor
import time

class Post(BaseModel):
    tittle: str
    content: str
    published: bool = True
while True:
    try: 
        conn = psycopg2.connect(host='localhost',database='fastapi',
        user='postgres',password='admin',cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was succesfull !!")
        break
    except Exception as error:
        print("Database connection was failed !!")
        print("Error: ", error)
        time.sleep(2)

my_posts = [{"tittle": "tittle of post 1", "content": "content of post 1", "id": 1},
    {"tittle": "tittle of post 2", "content": "content of post 2", "id": 2}]

def find_id(id):
    for p in my_posts:
        if p['id'] == id:
            return p

def find_index(id):
    for i, p in enumerate(my_posts):
        if p['id'] == id:
            return i

app = FastAPI()


@app.get("/")
def root():
    return {"message": "Hello World"}

@app.get("/posts")
def get_posts():
    cursor.execute("SELECT * FROM posts;")
    posts = cursor.fetchall()
    return {"post_detail": posts}

@app.post("/posts", status_code=status.HTTP_201_CREATED)
def create_posts(post: Post):
    cursor.execute("INSERT INTO posts (tittle, content, published) \
        VALUES (%s, %s, %s) RETURNING *", 
        (post.tittle, post.content, post.published))
    new_post = cursor.fetchone()
    conn.commit()
    return {"post_detail": new_post}

@app.get("/posts/{id}")
def get_post(id: int):
    cursor.execute("SELECT * FROM posts WHERE id = %s", (str(id)))
    post = cursor.fetchone()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id={id} was not found")
    return {"post_detail": post}

@app.delete("/posts/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int):
    cursor.execute("DELETE FROM posts WHERE id = %s RETURNING *", (str(id)))
    deleted_post = cursor.fetchone()
    conn.commit()
    if deleted_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post with id={id} was not found")
    return HTTPException(status_code=status.HTTP_204_NO_CONTENT,detail=f"deleted post {id}")

@app.put("/posts/{id}")
def update_post(id: int, post: Post):
    cursor.execute("UPDATE posts SET tittle = %s, content = %s, published = %s \
        WHERE id = %s RETURNING *", (post.tittle, post.content, post.published, str(id)))
    updated_post = cursor.fetchone()
    conn.commit()
    if updated_post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"post {id} was not found")
    return {"post_detail": updated_post}