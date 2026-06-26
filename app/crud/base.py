from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.config.database import Base
from app.utils.cache import query_cache, cache_key

ModelType = TypeVar("ModelType", bound=Base)

class CRUDBase(Generic[ModelType]):
    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.cache_ttl = 300  # 默认缓存时间5分钟

    def get(self, db: Session, id: Any, use_cache: bool = True) -> Optional[ModelType]:
        """获取单个对象"""
        cache_key_str = cache_key("get", model=self.model.__name__, id=id)
        
        if use_cache:
            cached = query_cache.get(cache_key_str)
            if cached is not None:
                return cached
        
        result = db.query(self.model).filter(self.model.id == id).first()
        
        if use_cache and result:
            query_cache.set(cache_key_str, result, self.cache_ttl)
        
        return result

    def get_multi(
        self, db: Session, *, skip: int = 0, limit: int = 100, use_cache: bool = False
    ) -> List[ModelType]:
        """获取多个对象"""
        return db.query(self.model).offset(skip).limit(limit).all()

    def get_multi_by_filter(
        self, db: Session, *, filters: Dict[str, Any], skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        """根据条件过滤获取多个对象"""
        query = db.query(self.model)
        for key, value in filters.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def create(self, db: Session, *, obj_in: Dict[str, Any]) -> ModelType:
        """创建对象"""
        db_obj = self.model(**obj_in)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        
        # 清除相关缓存
        self._invalidate_cache()
        
        return db_obj

    def update(
        self,
        db: Session,
        *,
        db_obj: ModelType,
        obj_in: Union[Dict[str, Any], ModelType]
    ) -> ModelType:
        """更新对象"""
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        
        for field in update_data:
            if hasattr(db_obj, field):
                setattr(db_obj, field, update_data[field])
        
        db.commit()
        db.refresh(db_obj)
        
        # 清除相关缓存
        self._invalidate_cache()
        
        return db_obj

    def remove(self, db: Session, *, id: Any) -> ModelType:
        """删除对象"""
        obj = db.query(self.model).get(id)
        db.delete(obj)
        db.commit()
        
        # 清除相关缓存
        self._invalidate_cache()
        
        return obj

    def count(self, db: Session) -> int:
        """统计记录数"""
        return db.query(func.count(self.model.id)).scalar()

    def exists(self, db: Session, **kwargs) -> bool:
        """检查是否存在满足条件的记录"""
        query = db.query(self.model)
        for key, value in kwargs.items():
            if hasattr(self.model, key):
                query = query.filter(getattr(self.model, key) == value)
        return query.first() is not None

    def _invalidate_cache(self) -> None:
        """使相关缓存失效"""
        # 清除所有与当前模型相关的缓存
        keys_to_delete = []
        for key in query_cache.cache:
            if key.startswith(f"get:model={self.model.__name__}"):
                keys_to_delete.append(key)
        
        for key in keys_to_delete:
            query_cache.delete(key)