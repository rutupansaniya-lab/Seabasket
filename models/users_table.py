from sqlalchemy import Column, String, DateTime, Integer, Boolean, func, Text
from config.db_config import Base

class Users(Base):
    __tablename__ = "users"   

    id = Column("id", Integer, primary_key=True, autoincrement=True)
    userName = Column("userName", String(255), unique=True, nullable=False)
    email = Column("email", String(255), unique=True, nullable=False)
    phoneNumber = Column("phoneNumber", String(20), unique=True, nullable=False)
    hashedPassword = Column("hashedPassword", String(255), nullable=False)
    roleId = Column("roleId", Integer, default=1)
    isDeleted = Column("isDeleted", Boolean, default=False)
    createdAt = Column("createdAt", DateTime, server_default=func.now())
    updatedAt = Column("updatedAt", DateTime,server_default=func.now(),onupdate=func.now())
    deletedAt = Column("deletedAt", DateTime, nullable=True)
    otp = Column("otp",String(6), nullable=True)
    otpExp = Column("otpExp",DateTime, nullable=True)
    credit_card_number=Column("credit_card_number",String(16), nullable=True)
    card_expiry = Column("card_expiry",String(10), nullable=True)
    card_cvv = Column("card_cvv",String(5), nullable= True)
    address = Column("address",Text, nullable=True)
    
users_table = Users.__table__