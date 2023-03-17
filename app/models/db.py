from typing import Optional
from sqlalchemy import Column, Float, Integer, LargeBinary, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


# create enum for each endpoint 

class Base(DeclarativeBase):
   pass


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    identifier = Column(String)
    email = Column(String, nullable=True)
    hashed_pw = Column(String, nullable = True)
    provider_id = Column(String, nullable = True)
    provider = Column(String)
    api_keys = relationship("ApiKey", back_populates="user", cascade='all, delete-orphan')
    credit_tracking = relationship("CreditTracking",  uselist=False, cascade="all, delete")

    
    def __repr__(self) -> str:
        return f"User( identifier= {self.identifier} provider_id = {self.provider_id}, provider={self.provider}, hashed_password = {self.hashed_pw})"

class ApiKey(Base):
    __tablename__ = 'api_keys'
    key = Column(String, primary_key=True)
    expiration_date = Column(String, nullable = True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'))
    user = relationship("User", back_populates="api_keys")


class CreditTracking (Base):
    __tablename__ = "credit_tracking"
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'), primary_key=True)
    credit = Column(Integer , default = 0)

    def __repr__(self) -> str:
        return f"CreditTracking( user_id = {self.user_id}, credit = {self.credit})"
    

class Blacklist(Base):
    __tablename__ = "blacklist"
    token = Column(String(200), primary_key=True)

    def __repr__(self) -> str:
        return f"Blacklist token={self.token!r})"



KUBER_ENDPOINTS_COST = {
    "/api/v1/tx" : 10,
    "/api/v1/time" : 20,
    "/api/v1/txs" : 5
}
