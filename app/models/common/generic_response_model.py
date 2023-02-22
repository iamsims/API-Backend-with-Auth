from datetime import datetime
from typing import Generic, Optional, TypeVar, Any

from pydantic import BaseModel
from pydantic.generics import GenericModel

DataT = TypeVar('DataT')
Content = TypeVar('Content')


class PageableModel(BaseModel):
    page: int = 0
    size: int = 15
    total: int = 0


class DataModel(BaseModel):
    content: DataT
    pageable: Optional[PageableModel] = None


class GenericResponseModel(GenericModel, Generic[Content]):
    apiVersion: str = 'v1'
    payload: Optional[DataModel | Content] = None
    timestamp: datetime = datetime.now().isoformat()
