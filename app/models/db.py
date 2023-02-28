from typing import Optional
from sqlalchemy import String
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column

class Base(DeclarativeBase):
   pass


'''
identifier consists of the username or email of the user
hashed_pw is the hashed password of the user
'''

class User(Base):
    __tablename__ = "users"
    identifier: Mapped[str]  = mapped_column(primary_key=True)
    hashed_pw: Mapped[Optional[str]]
    provider_id: Mapped[Optional[int]] = mapped_column(primary_key=True)
    provider: Mapped[str] = mapped_column( primary_key=True)
    
    def __repr__(self) -> str:
        return f"User( identifier= {self.identifier} provider_id = {self.provider_id}, provider={self.provider!r}, hashed_password = {self.hashed_pw})"


class Blacklist(Base):
    __tablename__ = "blacklist"
    token: Mapped[str] = mapped_column(String(200), primary_key=True)

    def __repr__(self) -> str:
        return f"Blacklist token={self.token!r})"


# FAKE_BLACKLIST = []

# def add_blacklist_token(token):
#     FAKE_BLACKLIST.append(token)
#     return True


# def is_token_blacklisted(token):
#     if token in FAKE_BLACKLIST:
#         return True
#     return False


