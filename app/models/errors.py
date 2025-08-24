from __future__ import annotations
from typing import Dict, List, Any
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from pydantic import ValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY

def _group_errors(exc: ValidationError | RequestValidationError) -> Dict[str, List[str]]:
    """
    Convert Pydantic/FastAPI validation errors into:
      { "<field>": ["msg1", "msg2"], "non_field_errors": ["msg"] }
    """
    field_map: Dict[str, List[str]] = {}
    for err in exc.errors():
        loc = err.get("loc", [])
        msg = err.get("msg", "Invalid value")

        # Choose the most specific string element in loc, skipping 'body'/'query'/'path'
        field = "non_field_errors"
        for part in reversed(loc):
            if isinstance(part, str) and part not in {"body", "query", "path"}:
                field = part
                break

        field_map.setdefault(field, []).append(msg)

    return field_map

def install_422_handlers(app: FastAPI) -> None:
    @app.exception_handler(RequestValidationError)
    async def _request_validation_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=_group_errors(exc),
        )

    @app.exception_handler(ValidationError)
    async def _pydantic_validation_handler(request: Request, exc: ValidationError):
        return JSONResponse(
            status_code=HTTP_422_UNPROCESSABLE_ENTITY,
            content=_group_errors(exc),
        )
