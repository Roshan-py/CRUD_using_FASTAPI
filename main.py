from fastapi_pagination import Page, add_pagination, paginate, LimitOffsetPage
from fastapi import FastAPI, Depends, Response, status, HTTPException
import models
import schemas
from database import engine, SessionLocal
from sqlalchemy.orm import Session
import logging


app = FastAPI()

models.Base.metadata.create_all(engine)


# dependency
def get_db():
    db = SessionLocal
    try:
        yield db
    finally:
        db.close()


# Creating Logging File
LOG_FORMAT = "%(levelname)s %(asctime)s - %(name)s - %(message)s"
logging.basicConfig(filename='C:/Users/roshan/Documents/FAST/blog/blog.log', level=logging.DEBUG,
                    format=LOG_FORMAT)

logger = logging.getLogger()


# Create
@app.post('/blog', status_code=201)
def create(request: schemas.Blog, db: Session = Depends(get_db)):
    new_blog = models.Blog(title=request.title, body=request.body)
    db.add(new_blog)
    db.commit()
    db.refresh(new_blog)
    logger.info('a new blog is created')
    return new_blog


'''
# READ
@app.get('/blog')
def allblog(db: Session = Depends(get_db)):
    blogs = db.query(models.Blog).all()
    return blogs
'''


# READ WITH PAGINATION
@app.get("/blog", response_model=Page[schemas.Blog])
@app.get("/blog/limit-offset", response_model=LimitOffsetPage[schemas.Blog])
def get_blogs(db: Session = Depends(get_db)):
    logger.info('displaying blogs')
    return paginate(db.query(models.Blog).all())


add_pagination(app)


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
        logger.error(
            HTTPException(status.HTTP_404_NOT_FOUND, f'blog with id  {id} is not available, Wrong id provided'))
        raise HTTPException(status.HTTP_404_NOT_FOUND, detail=f'blog with {id} is not available')
    logger.info(blog, f'blog with id {id} is displayed')
    return blog


# DELETE
@app.delete('/blog/{id}', status_code=status.HTTP_204_NO_CONTENT)
def delete(id, db: Session = Depends(get_db)):
    db.query(models.Blog).filter(models.Blog.id == id).delete(synchronize_session=False)  # documentation of sqlalchemy
    db.commit()
    logger.info(f'blog with id {id} is deleted')
    return {'done': 'delete operation executed successfully'}


# PUT
@app.put('/blog/{id}', status_code=status.HTTP_202_ACCEPTED)
def update(id, request: schemas.Blog, db: Session = Depends(get_db)):
    blog = db.query(models.Blog).filter(models.Blog.id == id)
    if not blog.first():
        logger.error(f'blog with id {id} is not found')
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f'blog with {id} not found')
    blog.update(request.dict())  # need to use dict to edit parameters
    db.commit()
    logger.info(f'updated blog with id  {id} successfully')
    return f'updated blog with id  {id} successfully..!!!'
