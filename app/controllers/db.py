import datetime
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from app.constants.exceptions import DATABASE_EXCEPTION
from app.models.db import Base, Blacklist, CreditTracking, User, ApiKey
from sqlalchemy import URL
from decouple import config

from app.models.users import UserinDB


DB_USERNAME = config('DB_USERNAME') or None
if DB_USERNAME is None:
    raise 'Missing DB_USERNAME'

DB_PASSWORD = config('DB_PASSWORD') or None
if DB_PASSWORD is None:
    raise 'Missing DB_PASSWORD'

DB_HOST = config('DB_HOST') or None
if DB_HOST is None:
    raise 'Missing DB_HOST'

DB_NAME = config('DB_NAME') or None
if DB_NAME is None:
    raise 'Missing DB_NAME'

url_object = URL.create(
    "postgresql+psycopg2",
    username=DB_USERNAME,
    password=DB_PASSWORD,  # plain (unescaped) text
    host=DB_HOST,
    database=DB_NAME,
)

engine = create_engine(url_object)
Base.metadata.create_all(engine)


async def add_api_key(id : int, api_key : str):
    try:
        with Session(engine) as session:
            # todo check if i can insert user directly without actually inserting it
            user = await get_user_by_id(id) 
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
            api_key = ApiKey(key=api_key, user=user, expiration_date=expiration_date, user_id=id)
            session.add(api_key)
            session.commit()

    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION


async def get_api_keys(id : int):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=id).first()
            api_keys = []
           
            for key in user.api_keys:
                print(key.expiration_date)
                if datetime.datetime.strptime(key.expiration_date, '%Y-%m-%d %H:%M:%S.%f') < datetime.datetime.now():
                    session.delete(key)
                    session.commit()

                else:
                    api_keys.append(key)

            return api_keys

    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION



async def add_user(data : UserinDB):
    try:
        with Session(engine) as session:
            user = User(identifier=data.identifier, email=data.email, hashed_pw=data.hashed_pw, provider_id=data.provider_id, provider=data.provider)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user.id

    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION


async def get_user_id_by_data(data : UserinDB):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(identifier=data.identifier, provider=data.provider).first()
            return user.id
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION
    

async def get_all_users():
    try:
        with Session(engine) as session:
            users = session.query(User).all()
            return users
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION

    
async def get_user_by_data(data : UserinDB):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(identifier=data.identifier, provider=data.provider).first()
            return user
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION



async def users_exists_by_id(id : int):
    try:
        user = await get_user_by_id(id)
        if user:
            return True
        return False
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION

async def get_user_by_id(id : int):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=id).first()
            return user
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION
    
async def users_exists_by_data(data : UserinDB):
    try:
        user = await get_user_by_data(data)
        if user:
            return True
        return False
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION


async def add_blacklist_token(id : int):
    try:
        with Session(engine) as session:
            token = Blacklist(token = id)
            session.add(token)
            session.commit()

    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION


async def is_token_blacklisted(id : int):
    try:
        with Session(engine) as session:
            token = session.query(Blacklist).filter_by(token=id).first()
            if token:
                return True
            return False
        
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION
    

async def add_credit_for_user(id : int, credit :int):
    try:
        with Session(engine) as session:
            credit_entry = CreditTracking (user_id=id, credit=credit)
            session.add(credit_entry)
            session.commit()
    
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION


async def get_credit_for_user(id : int):
    try:
        with Session(engine) as session:
            credit_entry = session.query(CreditTracking).filter_by(user_id=id).first()
            return credit_entry.credit
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION
    

async def decrement_endpoint_credit_for_user(id : int, cost :int):
    try:
        with Session(engine) as session:
            credit_entry = session.query(CreditTracking).filter_by(user_id=id).first()
            credit_entry.credit -= cost
            session.commit()
   
    except Exception as e :
        print(e)
        raise DATABASE_EXCEPTION