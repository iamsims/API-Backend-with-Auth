from pydantic import BaseModel

class Snippet(BaseModel):
    code : str
