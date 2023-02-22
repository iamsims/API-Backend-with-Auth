from fastapi import FastAPI, Body, Depends 
from app.model import PostSchema, UserSchema, UserLoginSchema
from app.auth.jwt_handler import signJWT
from app.auth.jwt_bearer import jwtBearer


app = FastAPI()

posts = [ 
    {
        "id" : 1,
        "title" : "My first post",
        "content" : "This is my first post."
    }, 
    {
        "id" : 2,
        "title" : "My second post",
        "content" : "This is my second post."
        
    }, 
    {
        "id" : 3,
        "title" : "My third post",
        "content" : "This is my third post."

    }
]


users = []


@app.get("/", tags=["test"])
async def root():
    return {"message" : "Hello World"}


@app.get("/posts", tags=["posts"])
async def get_posts():
    return {"posts" : posts}


@app.get("/posts/{post_id}", tags=["posts"])
async def get_post(post_id : int):
    if post_id > len(posts):
        return {
            "error": "Post not found"
        }
    for post in posts:
        if post["id"] == post_id:
            return {"post" : post}
    return {"error" : "Post not found"}


@app.post("/posts", tags=["posts"], dependencies=[Depends(jwtBearer())])
async def add_post(post : PostSchema):
    posts.append(post)
    return {"info" : "Post added successfully"}


@app.post("/user/signup", tags=["user"])
async def signup(user : UserSchema = Body(default=None)):
    users.append(user)
    return signJWT(user.email)


@app.post("/user/login", tags=["user"])
async def login(user : UserLoginSchema = Body(default=None)):
    for u in users:
        if u.email == user.email and u.password == user.password:
            return signJWT(user.email)
    return {"error" : "User not found"}









