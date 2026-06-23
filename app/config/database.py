from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

# 数据库连接池配置
engine = create_engine(
    DATABASE_URL,
    echo=True,
    pool_size=10,              # 初始连接池大小
    max_overflow=20,           # 最大溢出连接数
    pool_pre_ping=True,        # 连接前ping检测
    pool_recycle=3600,         # 连接回收时间（秒）
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()