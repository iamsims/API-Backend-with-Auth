from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.models.db import Base, User, Blacklist
from app.models.users import UserLoginSchema, UserinDB

engine = create_engine("sqlite:///users.db ")
Base.metadata.create_all(engine)



async def is_user_in_db(data : UserinDB):
    with Session(engine) as session:
        if data.provider == "password":
            user = session.query(User).filter_by(identifier=data.identifier, provider = data.provider).first()
        else:
            user = session.query(User).filter_by(identifier=data.identifier, provider = data.provider, provider_id = data.provider_id).first()
        if user:
            return True
        return False

async def add_user(data : UserinDB):
    with Session(engine) as session:
        if data.provider == "password":
            user = User(
                identifier = data.identifier, 
                hashed_pw =data.hashed_pw,
                provider = data.provider,
                provider_id = data.identifier
            )
        else:
            user = User(
            identifier = data.identifier, 
            email = data.email,
            hashed_pw =data.hashed_pw,
            provider = data.provider,
            provider_id = data.provider_id
        )

        # print(user)
        session.add(user)
        session.commit()

async def get_all_users():
    with Session(engine) as session:
        users = session.query(User).all()
        return users
    

async def get_user(data : UserinDB):
    with Session(engine) as session:
        user = session.query(User).filter_by(identifier=data.identifier, provider = data.provider, provider_id = data.provider_id).first()
        return user
    

async def add_blacklist_token(id : int):
    with Session(engine) as session:
        token = Blacklist(token = id)
        session.add(token)
        session.commit()


async def is_token_blacklisted(id : int):
    with Session(engine) as session:
        token = session.query(Blacklist).filter_by(token=id).first()
        if token:
            return True
        return False