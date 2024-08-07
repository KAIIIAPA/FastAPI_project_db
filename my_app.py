import hashlib
from sqlalchemy.orm import Session
from fastapi import FastAPI, Form
from fastapi.staticfiles import StaticFiles
from database import *
from utils.templating import TemplateResponse
from fastapi.responses import HTMLResponse
from fastapi import Request, Depends


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

@app.get(
    "/login/",
    name="login:login_page",
    response_class=HTMLResponse
)
def login_page(request: Request):
    return TemplateResponse(request=request, name="login_page.html")


@app.post(
    "/login/",
    name="login:login_page",
    response_class=HTMLResponse
    )
def login_page_user(request: Request, username: str = Form(), password: str = Form(), db: Session = Depends(get_db)):
    info = {}
    username = username
    password = password
    hashed_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    user = db.query(User).filter(User.username == username).first()
    if user.hashed_password == hashed_password:
        # как это сделать??
    else:
        info['error'] = 'Неправильное имя пользователя или пароль'
        return TemplateResponse(request=request, name="login_page.html", context=info)
