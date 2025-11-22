from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, JSON, ForeignKey
from sqlalchemy.sql import func
from app.core.database import Base

class Strategy(Base):
    __tablename__ = "strategies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    model_id = Column(Integer, ForeignKey("models.id"))
    is_active = Column(Boolean, default=False)
    is_paper = Column(Boolean, default=True)
    config = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class Model(Base):
    __tablename__ = "models"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    version = Column(String, nullable=False)
    params = Column(JSON)
    metrics = Column(JSON)
    artifact_uri = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
