from fastapi import FastAPI, Path
from typing import Annotated
from services.user import id

app = FastAPI(title="Api integrada com o FastMCP")
service = id()


@app.get("/{id}")
async def retorna_id(id: Annotated[int, Path()]):
    return service.retorna_id(id)