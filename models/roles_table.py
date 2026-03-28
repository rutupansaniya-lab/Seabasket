from sqlalchemy import Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

class Roles(Base):
    __tablename__ = "roles"
    
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(255), unique=True, nullable=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now())

