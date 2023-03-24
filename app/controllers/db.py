import datetime
import math
import sys
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session
from app.constants.exceptions import DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION
from app.models.db import Base, Blacklist, CreditTracking, LogEntry, User, ApiKey
from sqlalchemy import URL
from decouple import config
from sqlalchemy.exc import OperationalError

from app.models.users import UserinDB


DB_DRIVER = config('DB_DRIVER', default="postgresql+psycopg2")
DB_USERNAME = config('DB_USERNAME', default = None) 
DB_PASSWORD = config('DB_PASSWORD', default = None) 
DB_HOST = config('DB_HOST', default = None)
DB_NAME = config('DB_NAME', default= None)

if DB_DRIVER != "sqlite":
    if DB_USERNAME is None:
        raise 'Missing DB_USERNAME'

    if DB_PASSWORD is None:
        raise 'Missing DB_PASSWORD'

    if DB_HOST is None:
        raise 'Missing DB_HOST'

    if DB_NAME is None:
        raise 'Missing DB_NAME'


def startup_db():
    try:
        if DB_DRIVER == "sqlite":
            url_object = 'sqlite:///db.sqlite'
            
        else:
            url_object = URL.create(
            drivername= DB_DRIVER,
            username=DB_USERNAME,
            password=DB_PASSWORD,  # plain (unescaped) text
            host=DB_HOST,
            database=DB_NAME,
            )

        engine = create_engine(url_object)
        Base.metadata.create_all(engine)

        return engine 
    
    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def add_api_key(engine , id : int, api_key : str):
    try:
        with Session(engine) as session:
            # todo check if i can insert user directly without actually inserting it
            user = await get_user_by_id(engine, id) 
            expiration_date = datetime.datetime.now() + datetime.timedelta(days=30)
            api_key = ApiKey(key=api_key, user=user, expiration_date=expiration_date, user_id=id)
            session.add(api_key)
            session.commit()

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_api_keys(engine, id : int):
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
        
    except OperationalError as e:
        print(e)

        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)

        raise DATABASE_EXCEPTION    



async def add_user(engine, data : UserinDB):
    try:
        with Session(engine) as session:
            user = User(identifier=data.identifier, email=data.email, hashed_pw=data.hashed_pw, provider_id=data.provider_id, provider=data.provider)
            session.add(user)
            session.commit()
            session.refresh(user)
            return user.id

    except OperationalError as e:
        print(e)

        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_user_id_by_data(engine, data : UserinDB):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(identifier=data.identifier, provider=data.provider).first()
            return user.id

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    
 

async def get_all_users(engine):
    try:
        with Session(engine) as session:
            users = session.query(User).all()
            return users

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    

    
async def get_user_by_data(engine, data : UserinDB):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(identifier=data.identifier, provider=data.provider).first()
            return user
        
    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def users_exists_by_id(engine, id : int):
    try:
        user = await get_user_by_id(engine, id)
        if user:
            return True
        return False
    
    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    

async def get_user_by_id(engine, id : int):
    try:
        with Session(engine) as session:
            user = session.query(User).filter_by(id=id).first()
            return user
        
    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    
   
async def users_exists_by_data(engine, data : UserinDB):
    try:
        user = await get_user_by_data(engine, data)
        if user:
            return True
        return False

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_logs(engine, user_id: str, api_key : str =None, page: int = 1, page_size: int = 10):
    try:
        with Session(engine) as session:
            if not api_key:
                logs = session.query(LogEntry).filter_by(user_id=user_id).order_by(LogEntry.start_time.asc()).offset((page - 1) * page_size).limit(page_size).all()
                count = session.query(func.count(LogEntry.id)).filter_by(user_id=user_id).scalar()  
            else:
                logs = session.query(LogEntry).filter_by(user_id=user_id, api_key=api_key).order_by(LogEntry.start_time.asc()).offset((page - 1) * page_size).limit(page_size).all()
                count = session.query(func.count(LogEntry.id)).filter_by(user_id=user_id, api_key=api_key).scalar()

            result = []
            for log in logs:
                log.request_headers = None
                log.response_headers = None
                result.append(log)
            
            total_size = math.ceil(count / page_size)

            return {
                "logs": result,       
                "total_pages": total_size, 
                "page": page,
                "page_size": page_size
            }
            
           
    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def add_blacklist_token(engine, id : int):
    try:
        with Session(engine) as session:
            token = Blacklist(token = id)
            session.add(token)
            session.commit()

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def is_token_blacklisted(engine, id : int):
    try:
        with Session(engine) as session:
            token = session.query(Blacklist).filter_by(token=id).first()
            if token:
                return True
            return False

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def add_credit_for_user(engine, id : int, credit :int):
    try:
        with Session(engine) as session:
            credit_entry = CreditTracking (user_id=id, credit=credit)
            session.add(credit_entry)
            session.commit()

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_credit_for_user(engine, id : int):
    try:
        with Session(engine) as session:
            credit_entry = session.query(CreditTracking).filter_by(user_id=id).first()
            return credit_entry.credit

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def decrement_endpoint_credit_for_user(engine, id : int, cost :int):
    try:
        with Session(engine) as session:
            credit_entry = session.query(CreditTracking).filter_by(user_id=id).first()
            credit_entry.credit -= cost
            session.commit()

    except OperationalError as e:
        print(e)
        raise DATABASE_DOWN_EXCEPTION
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    
