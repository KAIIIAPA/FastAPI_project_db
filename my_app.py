import hashlib
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from database import *
from utils.templating import TemplateResponse
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends
from fastadmin import fastapi_app as admin_app


# создаем таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")


# определяем зависимость
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get(
    "/",
    response_class=HTMLResponse,
    name='main:main_page')
def main_page(request: Request, db: Session = Depends(get_db)):
    news = db.query(NewsFilm).order_by(NewsFilm.created_at.desc()).all()
    news = news[:2]
    context = {
        'news': news
    }
    return TemplateResponse(request=request, name='main_page.html', context=context)

@app.get(
    "/news/",
    name="news:page_news",
    response_class=HTMLResponse
)
def news_page(request: Request, db: Session = Depends(get_db)):
    news = db.query(NewsFilm).order_by(NewsFilm.created_at.desc()).all()
    context = {
        'news': news
    }
    return TemplateResponse(request=request, name="news_page.html", context=context)


@app.get(
    "/news/{id}",
    name="new:page_new",
    response_class=HTMLResponse
)
def new_page(id, request: Request, db: Session = Depends(get_db)):
    news = db.query(NewsFilm).filter_by(id=id).first()
    print(news.id)
    context = {
        "news": news
    }
    return TemplateResponse(request=request, name="new_page.html", context=context)

@app.get(
    "/registration/",
    name="registration:page_registration",
    response_class=HTMLResponse
)
def registration_page(request: Request):
    return TemplateResponse(
        request=request,
        name="registration_page.html",
    )


@app.post(
    "/registration/",
    name="registration:page_registration",
    response_class=HTMLResponse
)
def registration_user_page(request: Request, username: str = Form(), password: str = Form(), repeat_password: str = Form(),
                           age: int = Form(), email: str = Form(), db: Session = Depends(get_db)):
    users_list = set()
    email_list = set()
    username = username
    password = password
    repeat_password = repeat_password
    age = age
    email = email
    users_all = db.query(User).all()
    info = {}
    for usr in users_all:
        users_list.add(usr.username)
        email_list.add(usr.email)
    if username in users_list:
        info['error'] = 'Такой пользователь уже зарегистрирован'
        return TemplateResponse(request=request, name="registration_page.html", context=info)
    elif email in email_list:
        info['error'] = 'Такой email уже зарегистрирован'
        return TemplateResponse(request=request, name="registration_page.html", context=info)
    elif repeat_password != password:
        info['error'] = 'Пароли не совпадают'
        return TemplateResponse(request=request, name="registration_page.html", context=info)
    elif int(age) < 16:
        info['error'] = 'Вы должны быть старше 16'
        return TemplateResponse(request=request, name="registration_page.html", context=info)
    else:
        hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()  # шифруем пароль в sha-256
        user_ = User(username=username, hashed_password=hashed_password, email=email)
        db.add(user_)
        db.commit()
        return TemplateResponse(request=request, name="registration_page.html",
                                context={'wellcome': f'Поздравляю вы зарегистрированы, теперь можете авторизоваться'})

# Реализуем отдельный CRUD для модели NewsFilm
@app.post("/NewsFilm/")
def creat_NewsFilm(title: str, summary: str, img_url: str, description: str, db: Session = Depends(get_db)):
    news = NewsFilm(title=title, summary=summary, description=description, img_url=img_url)
    db.add(news)  # добавляем в бд
    db.commit()
    return "Новость добавлена"

@app.get("/NewsFilm/")
def read_NewsFilm(db: Session = Depends(get_db)):
    news = db.query(NewsFilm).order_by(NewsFilm.created_at.desc()).all()
    return news

@app.put("/NewsFilm/")
def update_NewsFilm(id: int, title: str, summary: str, img_url: str, description: str, db: Session = Depends(get_db)):
    news = db.query(NewsFilm).filter(NewsFilm.id == id).first()
    if news is not None:
        news.title = title
        news.summary = summary
        news.description = description
        news.img_url = img_url
        db.commit()  # сохраняем изменения
        # проверяем, что изменения применены в бд - получаем один объект
        new_news = db.query(NewsFilm).filter(NewsFilm.id == id).first()
        return f'Новость обновлена {new_news}'
    else:
        return f'Новости с таким id {id} не существует'

@app.delete("/NewsFilm/")
def delete_NewsFilm(id: int, db: Session = Depends(get_db)):
    news = db.query(NewsFilm).filter(NewsFilm.id == id).first()
    db.delete(news)
    db.commit()
    return 'Новость удалена'
