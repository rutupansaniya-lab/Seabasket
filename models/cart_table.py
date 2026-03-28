from sqlalchemy import Float, Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

# class UserCart(Base):

#     __tablename__ = "carts"

#     id = Column("id", Integer, primary_key=True, autoincrement=True)
#     user_id = Column("user_id", Integer, nullable=False)
#     createdAt = Column("createdAt", DateTime, server_default=func.now())
#     updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now())

class CartItem(Base):

    __tablename__ = "cart_item"


    id = Column("id", Integer, primary_key=True, autoincrement=True)
    userId = Column("userId", Integer, nullable=False)
    productId = Column("productId", Integer, nullable=False)
    quantity = Column("quantity", Integer, default=1)
    size=Column("size",String(50),nullable=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now())
    