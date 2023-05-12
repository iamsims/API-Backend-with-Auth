from pydantic import BaseModel

class Snippet(BaseModel):
    code : str
    lang : str or None = None
