from ast import List
import datetime
import json
import math
import time
from app.constants.exceptions import DATABASE_EXCEPTION
from prisma.errors import UniqueViolationError
from app.db.prisma import prisma
from app.models.users import UserinDB
from app.models.snippet import UpdateSnippet, CreateSnippet, UpdateSnippetName



async def get_snippet(snippet_id):
    try:
        snippet = await prisma.snippet.find_unique(
            where={"id": snippet_id}
        )
        return snippet
    
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION
    

async def create_snippet(snippet: CreateSnippet, snippet_id : str, user_id: int) -> int:
    try:
        db_snippet = await prisma.snippet.create(
            {"id" : snippet_id, "code": snippet.code, "user_id": user_id, "lang": snippet.lang, "name": snippet.name}
        )
        return db_snippet.id
        
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION
 

async def update_snippet(snippet_id: str, snippet: UpdateSnippet) :
    try:
        return await prisma.snippet.update(
        where={"id": snippet_id},
        data={"code": snippet.code},
        )
        
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def update_snippet_name(snippet_id: int, snippet: UpdateSnippetName) :
    try:
        return await prisma.snippet.update(
        where={"id": snippet_id},
        data={"name": snippet.name},
        )
        
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def delete_snippet(snippet_id: str):
    try:
        await prisma.snippet.delete(where={"id": snippet_id})
        return 
        
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def get_user( data: UserinDB):
    try:
        if data.provider == "password":
            user = await prisma.users.find_first(
                where={
                    "identifier": data.identifier,
                }
            )
        
        else :
            user = await prisma.users.find_first(
                where={
                "email": data.email,
                }
            )

        return user

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def add_user_identity(id , data: UserinDB, provider_data):
    try:
        print(provider_data)
        jsondata = json.dumps(provider_data)
        identity = await prisma.user_identities.create(data={
            "user_id": id,
            "provider": data.provider,
            "provider_id": data.provider_id,
            "provider_data": jsondata
        })
        return identity.user_id

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION


async def get_user_identity_by_provider(id : int, provider : str):
    try:
        user = await prisma.user_identities.find_first(
            where = {
            "user_id": id,
            "provider": provider
            }
        )

        return user

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def add_user( data: UserinDB, provider_data = None):
    try:
        user =   await prisma.users.create(data={
        'identifier': data.identifier,
        'email': data.email,
        'hashed_pw': data.hashed_pw,
        'provider': data.provider,
        'image': data.image
        })

        if provider_data:
            await add_user_identity(user.id, data, provider_data)
       

        return user.id

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def create_signup_credit_for_user( id : int, credit :int, provider : str):
    provider_data = {
            'signup_provider': provider            
            }
    
    jsondata = json.dumps(provider_data)
    try:
        credit_initial_purchase = await prisma.credit_purchase.create(
            data={
            "user_id": id,
            "credit_amount": credit,
            "created_date" : math.floor(time.time()*1000), 
            "payment_details" :  jsondata,
            "payment_method": "Beta Tester Pack"
            }
        )

        await prisma.credit_tracking.create(
            data = {
            "credit": credit_initial_purchase.credit_amount,
            "user_id": id 
            }
        )

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION    

async def is_token_blacklisted(id):
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
 

async def get_user_by_id(id : int):
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


async def add_blacklist_token(token : str):
    try:
        await prisma.blacklist.create(
            data ={
            "token": token,
        })

    except UniqueViolationError as e:
        print("Token already blacklisted")
        return

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
        if key:
            return key.user_id
        return None
      
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def add_log_entry(start_time, user_id, ip_address, end_time = None, request_headers = None, cost = 0, api_key = None, endpoint = None, method = None, status_code = None,  response_headers = None):
    try:
        if request_headers is None:
            request_headers = {}

        if response_headers is None:
            response_headers = {}

        log = await prisma.logs.create(
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
            "request_headers": json.dumps(dict(request_headers)),
            "response_headers": json.dumps(dict(response_headers))

        })
        # 
        return log.id
     
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION
    
async def increment_cost_for_log_entry(log_id, cost):
    try:
        await prisma.logs.update(
            where={
                "id": log_id,
            },
            data={
                "cost": {
                "increment": cost
                }
            }
        )
    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION

async def complete_log_entry(log_id, end_time, response_headers = None):
    try:
        if response_headers is None:
            response_headers = {}

        log = await prisma.logs.update(
            where={
                "id": log_id,
            },
            data={
                "end_time": end_time,
                "response_headers": json.dumps(dict(response_headers))
            }
        )


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
                    "start_time": "desc"
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
    

async def get_credit_purchase_history(id:int):
    try:
       credit_purchase_history = await prisma.credit_purchase.find_many(
           where={
               "user_id": id,
           },
           order={
           "created_date": "desc"
           
           }
       )

       credit_purchase_history_filtered = [
           {
           "credit_amount": entry.credit_amount,
           "created_date" : entry.created_date,
           "payment_method" : entry.payment_method,
           "payment_details": entry.payment_details
           } for entry in credit_purchase_history
       ]
       
       return credit_purchase_history_filtered

    except Exception as e:
        print(e)
        raise DATABASE_EXCEPTION   


