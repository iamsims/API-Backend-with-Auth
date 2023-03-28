from typing import Optional
from sqlalchemy import Column, Float, Integer, LargeBinary, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, relationship


# create enum for each endpoint 

class Base(DeclarativeBase):
   pass



class LogEntry(Base):
    __tablename__ = 'logs'

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    start_time = Column(Integer)
    duration = Column(Integer)
    ip_address = Column(String)
    status_code = Column(Integer)
    request_headers = Column(LargeBinary)
    response_headers = Column(LargeBinary)
    method = Column(String)
    endpoint = Column(String)
    cost = Column(Float)
    api_key = Column(String, ForeignKey('api_keys.key'))
    user_id = Column(Integer, ForeignKey('users.id'))
    
    def __repr__(self) -> str:
        return f"LogEntry(start_time = {self.start_time}, duration={self.duration!r}, ip_address = {self.ip_address}, status_code = {self.status_code}, api_key = {self.api_key}, method = {self.method}, endpoint = {self.endpoint}, cost = {self.cost})"

 

class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    identifier = Column(String)
    email = Column(String, nullable=True)
    hashed_pw = Column(String, nullable = True)
    provider_id = Column(String, nullable = True)
    provider = Column(String)
    api_keys = relationship("ApiKey", back_populates="user", cascade='all, delete-orphan')
    credit_tracking = relationship("CreditTracking",  uselist=False, cascade="all, delete-orphan")

    
    def __repr__(self) -> str:
        return f"User( identifier= {self.identifier} provider_id = {self.provider_id}, provider={self.provider}, hashed_password = {self.hashed_pw})"

class ApiKey(Base):
    __tablename__ = 'api_keys'
    key = Column(String, primary_key=True)
    expiration_date = Column(String, nullable = True)
    user_id = Column(Integer, ForeignKey('users.id', ondelete = 'CASCADE'))
    user = relationship("User", back_populates="api_keys")
    name = Column(String, nullable = True)
    created = Column(String, nullable = True)


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
