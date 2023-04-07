# import datetime
# import math
# import sys
# from sqlalchemy import create_engine, func
# from sqlalchemy.orm import Session
# from app.constants.exceptions import DATABASE_DOWN_EXCEPTION, DATABASE_EXCEPTION
# from app.models.db import Base, Blacklist, CreditTracking, LogEntry, User, ApiKey
# from sqlalchemy import URL
# from decouple import config
# from sqlalchemy.exc import OperationalError

# import pickle
# from fastapi import status 


# from decouple import config
# from app.models.db import  LogEntry

import datetime
import math
import time
from app.constants.exceptions import DATABASE_EXCEPTION
from app.db.prisma import prisma
from app.models.users import UserinDB


async def get_user_by_data( data: UserinDB):
    try:
        user = await prisma.users.find_first(
            where={
                "identifier": data.identifier,
                "provider": data.provider,
            }
        )
        return user

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def users_exists_by_data( data: UserinDB):
    try:
        user = await get_user_by_data(data)
        if user:
            return True
        return False

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def add_user( data: UserinDB):
    try:
        user =   await prisma.users.create(data={
        'identifier': data.identifier,
        'email': data.email,
        'hashed_pw': data.hashed_pw,
        'provider': data.provider,
        'provider_id': data.provider_id,
        'image': data.image

    })
        return user.id

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def create_credit_for_user( id : int, credit :int):
    try:
        await prisma.credit_tracking.create(
            data={
            "user_id": id,
            "credit": credit,
        })

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    

async def get_user_id_by_data( data: UserinDB):
    try:
        user = await prisma.users.find_first(
            where={
                "identifier": data.identifier,
            }
        )
        return user.id

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def is_token_blacklisted( id):
    try:
        token = await prisma.blacklist.find_unique(
            where={
                "token": id,
            }
        )
        if token:
            return True
        return False

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def users_exists_by_id( id : int):
    try:
        user = await get_user_by_id(id)
        if user:
            return True
        return False
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    

async def get_user_by_id( id : int):
    try:
        user = await prisma.users.find_unique(
            where={
                "id": id,
            }
        )
        return user
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def add_blacklist_token( id : int):
    try:
        await prisma.blacklist.create(
            data ={
            "token": id,
        })

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    



async def get_api_keys(id : int):
    try:
        keys = await prisma.api_keys.find_many(
            where={
                "user_id": id,
            }
        )

        now = time.time()*1000 # in milliseconds
        for key in keys:
            if key.expiration_date and key.expiration_date < now:
                await delete_api_key(key.key)
                keys.remove(key)
        
        keys = [key.key for key in keys]

        return keys
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_user_id_by_api_key(api_key : str):
    try:
        key = await prisma.api_keys.find_unique(
            where={
                "key": api_key,
            }
        )
        return key.user_id
      
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def add_log_entry(start_time, end_time, ip_address, cost, user_id, api_key = None, endpoint = None, method = None, status_code = None, request_headers = None, response_headers = None):
    try:
        await prisma.logs.create(
            data={
            "start_time": start_time,
            "end_time": end_time,
            "ip_address": ip_address,
            "cost": cost,
            "user_id": user_id,
            "api_key": api_key,
            "endpoint": endpoint,
            "method": method,
            "status_code": status_code,
            "request_headers": request_headers,
            "response_headers": response_headers

        })
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION



async def add_api_key( id : int, api_key : str, name : str = None):
    try:
        created = math.floor(time.time()*1000) # in milliseconds
        expiration_date = created + 60 * 60 * 24 * 30 * 1000 # in milliseconds

        await prisma.api_keys.create(
            data={
            "key": api_key,
            "user_id": id,
            "expiration_date": expiration_date,
            "created": created,
            "name": name,
        })

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def delete_api_key(api_key : str):
    try:
        await prisma.api_keys.delete(
            where={
                "key": api_key,
            }
        )
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION



async def get_logs(user_id: str, api_key : str =None, page: int = 1, page_size: int = 10):
    try:
        if not api_key:
            logs = await prisma.logs.find_many(
                where={
                    "user_id": user_id,
                },
                skip=(page - 1) * page_size,
                take=page_size,
                order={
                    "end_time": "desc"
                }
            )
            count = await prisma.logs.count(
                where={
                    "user_id": user_id,
                }
            )
        else:
            logs = await prisma.logs.find_many(
                where={
                    "user_id": user_id,
                    "api_key": api_key,
                },
                skip=(page - 1) * page_size,
                take=page_size,
                order={
                    "end_time": "desc"

                }
            )
            count = await prisma.logs.count(
                where={
                    "user_id": user_id,
                    "api_key": api_key,
                }
            )
       
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
            
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def get_credit_for_user(id : int):
    try:
        credit_entry = await prisma.credit_tracking.find_unique(
            where={
                "user_id": id,
            }
        )
        return credit_entry.credit
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    


async def decrement_credit_for_user(id : int, cost :int):
    try:
        credit_entry = await prisma.credit_tracking.find_unique(
            where={
                "user_id": id,
            }
        )
        credit_entry.credit -= cost
        await prisma.credit_tracking.update(
            where={
                "user_id": id,
            },
            data={
                "credit": credit_entry.credit,
            }
        )
        return credit_entry.credit
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    
