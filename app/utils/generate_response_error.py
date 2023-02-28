from app.models.common.generic_response_model import DataModel, PageableModel


def generate_generic_pageable_response(data):
    payload: DataModel = DataModel()
    pageable: PageableModel = PageableModel()
    if isinstance(data, list):
        pageable.total = len(data)

    payload.pageable = pageable
    payload.content = data
    return payload
