from sqlalchemy import Float, Table, Column, String, Text, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

class Orders(Base):
    __tablename__ = "orders"
    
    id = Column("id", Integer, primary_key=True,autoincrement=True)
    userId = Column("userId", Integer, nullable=False)
    shippingAddressId=Column("shippingAddressId",Text, nullable=False)
    totalAmount=Column("totalAmount",Float, nullable=False)
    orderStatus=Column("orderStatus",String, nullable=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(),onupdate=func.now())


class OrderItems(Base):
    __tablename__ = "order_items"
    
    id = Column("id", Integer, primary_key=True,autoincrement=True)
    orderId = Column("orderId", Integer, nullable=False)
    productId=Column("productId",Integer, nullable=False)
    quantity=Column("quantity",Integer, nullable=False)
    totalAmount=Column("totalAmount",Float, nullable=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(),onupdate=func.now())


