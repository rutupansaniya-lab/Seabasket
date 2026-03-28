from sqlalchemy import Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

class Address(Base):

    __tablename__ = "addresses"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    userId = Column("userId", Integer, nullable=False)
    addressLine1 = Column("addressLine_1", String(255), nullable=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now())


