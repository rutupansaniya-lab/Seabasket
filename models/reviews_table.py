from sqlalchemy import Float, Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

class ProductReview(Base):

    __tablename__ = "reviews"

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    productId = Column("productId", Integer, nullable=False)
    userId = Column("userId", Integer, nullable=False)
    rating = Column("rating", Float, nullable=False)
    comment = Column("comment",String(500), nullable=True)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now())


