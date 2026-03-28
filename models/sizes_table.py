from sqlalchemy import Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base

class ProductSizes(Base):
    __tablename__ = "product_sizes"
    
    id = Column("id", Integer, primary_key=True)
    productId = Column("productId", Integer, nullable=False)
    small_size_stock = Column("small_size_stock", Integer, default=0)
    medium_size_stock = Column("medium_size_stock", Integer, default=0)     
    large_size_stock = Column("large_size_stock", Integer, default=0)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(), onupdate=func.now()) 



product_sizes = ProductSizes.__table__