from sqlalchemy import Float, Table, Column, String, func
from sqlalchemy.sql.sqltypes import DateTime, Integer, Boolean
from config.db_config import Base
from sqlalchemy.dialects.mysql import LONGTEXT

class Products(Base):
    __tablename__ = "products"
    
    id = Column("id", Integer, primary_key=True)
    name = Column("name", String(255), unique=True, nullable=False)
    price = Column("price", Integer, nullable=False)
    description = Column("description", String(255), nullable=True)
    categoryId = Column("categoryId", Integer, nullable=False)
    isTrending = Column("isTrending", Boolean, default=False)
    imageUrl = Column("imageUrl", LONGTEXT, nullable=True)
    averageRating = Column("averageRating", Float, nullable=True) #added
    discountPercentage = Column("discountPercent", Float, default=0.0) #added
    small_size_stock = Column("small_size_stock",Integer, default=0)
    medium_size_stock = Column("medium_size_stock",Integer, default=0)
    large_size_stock = Column("large_size_stock",Integer, default=0)
    extra_large_size_stock = Column("extra_large_size_stock",Integer, default=0)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(),onupdate=func.now())
    

products_table = Products.__table__

