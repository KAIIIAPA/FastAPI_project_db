from sqlalchemy import Column, Integer, String, Text, TIMESTAMP, Boolean
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import create_engine
from datetime import datetime


# строка подключения
SQLALCHEMY_DATABASE_URL = "sqlite:///./database.db"

# создаем движок SqlAlchemy
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)


# создаем базовый класс для моделей
class Base(DeclarativeBase):
    pass


# создаем модель, объекты которой будут храниться в бд

class NewsFilm(Base):
    __tablename__ = "NewsFilm"

    id = Column(Integer, primary_key=True)
    title = Column(String(150), unique=True, nullable=False)
    summary = Column(String(250), unique=True, nullable=False)
    description = Column(Text(), unique=True, nullable=False)
    created_at = Column(TIMESTAMP(), default=datetime.utcnow)
    img_url = Column(Text(), unique=True, nullable=False)


class User(Base):
    __tablename__ = "User"

    id = Column(Integer, primary_key=True)
    username = Column(String(250), unique=True, nullable=False)
    email = Column(String(250), unique=True, nullable=False)
    role = Column(String(30), default="User")
    hashed_password = Column(String(250), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    is_superuser = Column(Boolean, default=False, nullable=False)
    is_verified = Column(Boolean, default=False, nullable=False)


# создаем сессию подключения к бд
SessionLocal = sessionmaker(autoflush=False, bind=engine)
