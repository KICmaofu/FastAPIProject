from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from app.config.settings import settings

DATABASE_URL = f"mysql+pymysql://{settings.DB_USER}:{settings.DB_PASSWORD}@{settings.DB_HOST}:{settings.DB_PORT}/{settings.DB_NAME}?charset=utf8mb4"

# 数据库连接池配置
engine = create_engine(
    DATABASE_URL,
    echo=False,                 # 生产环境关闭echo日志以提升性能
    pool_size=20,              # 初始连接池大小 - 根据预期并发量调整
    max_overflow=50,           # 最大溢出连接数 - 处理突发流量
    pool_pre_ping=True,        # 连接前ping检测 - 确保连接有效性
    pool_recycle=1800,         # 连接回收时间（秒）- 缩短回收周期避免连接失效
    pool_timeout=30,           # 获取连接超时时间（秒）
    max_identifier_length=128, # 最大标识符长度
    isolation_level="READ COMMITTED",  # 事务隔离级别
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()