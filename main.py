from fastapi import FastAPI, Depends, Response, status, HTTPException
import models
import schemas

from database import engine, SessionLocal
from sqlalchemy.orm import Session

app = FastAPI()

models.Base.metadata.create_all(engine)


# dependency
def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


# Create
@app.post('/blog', status_code=201)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    return new_blog


# READ
@app.get('/blog')
def allblog(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs


# READ WITH ID
@app.get('/blog/{id}')
def show(id, response: Response, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(
        models.Blog.id == id).first()  # in sqlalchemey we have comman filter operation so we use filter
    if not blog:
        '''
        response.status_code = status.HTTP_404_NOT_FOUND
       return {"msg":f"blog with {id} is not available"}
       '''
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'blog with {id} is not available')
    return blog


# DELETE
@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)  # documentation of sqlalchemy
    db.commit()
    return {'done': 'delete operation executed successfully'}


# PUT
@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'blog with {id} not found')
    blog.update(request.dict())  # need to use dict to edit parameters
    db.commit()
    return 'updated'
