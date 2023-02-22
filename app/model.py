from pydantic import BaseModel, Field, EmailStr


class PostSchema(BaseModel):
    id : int = Field(default=None)
    title : str = Field(default=None)
    content : str = Field(default=None)
    class Config:
        schema_extra = {
            "post_demo" : {
                "title" : "demo post",
                "content" : "This is my demo post."
            }
        }


class UserSchema(BaseModel):
    fullname : str = Field(default=None)
    email : EmailStr = Field(default=None)
    password : str = Field(default=None)
    class Config:
        schema_extra = {
            "user_demo" : {
                "fullname" : "John Doe",
                "email" : "", 
                "password" : ""
            }
        }


class UserLoginSchema(BaseModel):
    email : EmailStr = Field(default=None)
    password : str = Field(default=None)
    class Config:
        schema_extra = {
            "user_demo" : {
                "email" : "", 
                "password" : ""
            }
        }

    