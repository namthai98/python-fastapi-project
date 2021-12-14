from fastapi import FastAPI, Response, HTTPException, status, Depends, APIRouter
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from sqlalchemy.sql.functions import mode, user
from .. import models, schemas, oauth2
from ..database import get_db

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

# @router.get("/")
@router.get("/", response_model=List[schemas.Vote_out])
def get_posts(db: Session = Depends(get_db), current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
   #post = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
   post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()
   return post 

@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_posts(post: schemas.CreatedPost, db: Session = Depends(get_db), 
current_user: int = Depends(oauth2.get_current_user)):
    new_post = models.Post(owner_id=current_user.id,**post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post

@router.get("/{id}", response_model=schemas.Vote_out)
def get_post(id: int, db: Session = Depends(get_db),
current_user: int = Depends(oauth2.get_current_user)):
    #post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post, func.count(models.Votes.post_id).label("votes")).join(models.Votes, models.Votes.post_id == models.Post.id, isouter=True).group_by(models.Post.id).filter(models.Post.id == id).first()

    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post id={id} was not found")
    return post

@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int, db: Session = Depends(get_db),
current_user: int = Depends(oauth2.get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id)
    if post.first() == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post id={id} was not found")
    if post.first().owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail=f"Not authorized to perform requested action !")
    post.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.put("/{id}",response_model=schemas.Post)
def update_post(id: int, updated_post: schemas.CreatedPost, db: Session = Depends(get_db),
current_user: int = Depends(oauth2.get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Post id={id} was not found")
    post_query.update(updated_post.dict(), synchronize_session=False)
    db.commit()
    return post_query.first()