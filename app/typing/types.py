from typing import Union, AbstractSet, Mapping, Any, Generator, Tuple

IntStr = Union[int, str]
AbstractSetIntStr = AbstractSet[IntStr]
MappingIntStrAny = Mapping[IntStr, Any]
TupleGenerator = Generator[Tuple[str, Any], None, None]
