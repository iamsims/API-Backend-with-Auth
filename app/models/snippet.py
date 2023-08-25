from pydantic import BaseModel

class CreateSnippet(BaseModel):
    code : str
    lang : str 
    name : str


class UpdateSnippet(BaseModel):
    code: str 


class UpdateSnippetName(BaseModel):
    name : str
