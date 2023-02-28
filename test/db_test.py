import pytest 
# from ../db import is_user_in_db, add_user

# import db file from parent directory
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from db import is_user_in_db, add_user



@pytest.mark.asyncio
async def test_is_user_in_db():
    data = {"identifier": "test", "hashed_pw": "test", "provider": "password", "provider_id": ""}
    assert await is_user_in_db(data) == False