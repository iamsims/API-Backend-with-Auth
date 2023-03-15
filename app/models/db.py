from typing import Optional
from sqlalchemy import BigInteger, Column, ForeignKey, Integer, String
from sqlalchemy.orm import DeclarativeBase, relationship
from enum import Enum


class Base(DeclarativeBase):
   pass

'''
identifier consists of the username or email of the user
hashed_pw is the hashed password of the user
'''

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    identifier = Column(String)
    email = Column(String, nullable=True)
    hashed_pw = Column(String, nullable = True)
    provider_id = Column(String, nullable = True)
    provider = Column(String)
    api_keys = relationship("ApiKey", back_populates="user", cascade='all, delete-orphan')
    credit_tracking = relationship("CreditTracking", back_populates="user", cascade='all, delete-orphan')
    
    def __repr__(self) -> str:
        return f"User( identifier= {self.identifier} provider_id = {self.provider_id}, provider={self.provider}, hashed_password = {self.hashed_pw})"

class ApiKey(Base):
    __tablename__ = 'api_keys'
    key = Column(String, primary_key=True)
    expiration_date = Column(String)
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'))
    user = relationship("User", back_populates="api_keys")

class Blacklist(Base):
    __tablename__ = "blacklist"
    token = Column(String(200), primary_key=True)

    def __repr__(self) -> str:
        return f"Blacklist token={self.token!r})"


class CreditTracking (Base):
    __tablename__ = "credit_tracking"
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'), primary_key=True)
    user = relationship("User", back_populates="credit_tracking")
    endpoint1 = Column(Integer)
    endpoint2 = Column(Integer)
    endpoint3 = Column(Integer)

    def __repr__(self) -> str:
        return f"CreditTracking( user_id = {self.user_id})"
    



KUBER_ENDPOINTS_IN_DB = {
    "api/v1/tx" : "endpoint1",
    "api/v1/time" : "endpoint2",
    "api/v1/txs" : "endpoint3"
}

