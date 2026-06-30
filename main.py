from typing import Annotated, Optional
from enum import Enum
from pydantic import AfterValidator, Field, BaseModel, EmailStr

from fastapi import FastAPI, Header, Path, Query, Body, Cookie, Response

from fastapi.responses import JSONResponse, RedirectResponse

app = FastAPI(
    title="Site bacana",
    description="## **Testes na API**",
    summary="Aqui é onde estou estudando como funciona uma API",
    version="1.0.0",
)


class Fruta(Enum):
    banana = "banana"
    laranja = "laranja"


class Filtro(BaseModel):
    model_config = {"extra": "forbid"}

    limite: int = Field(100, gt=0, le=100)
    offset: int = Field(0, ge=0)


class Comentario(BaseModel):
    assunto: str
    comentario: str


class Post(BaseModel):
    titulo: str
    conteudo: str
    publicado: bool = True
    nota: int | None = None
    comentarios: Optional[list[Comentario]] = None


ITEM_ID_VALIDATION = Annotated[
    int,
    Path(
        title="ola",
        ge=5,
        examples=[4, 1],
    ),
]
QUERY_ID = Annotated[int, Query(gt=10)]

FRUTAS = Annotated[list[Fruta] | None, Query()]


class ModeloPost(BaseModel):
    titulo: str = Field(title="titulo da postagem", max_length=100)
    conteudo: str = Field(title="Conteudo da postagem", max_length=255)
    publicado: bool = True
    nota: int | None = Field(default=None, ge=0, le=10)


AnnotatedPath = Annotated[int, Path(ge=1, title="post ID")]
AnnotatedQuery = Annotated[bool, Query(description="notificar atualização")]
AnnotatedBody = Annotated[ModeloPost, Body()]


class UserIn(BaseModel):
    usuario: str
    email: EmailStr
    nome_completo: str | None = None


class UserPass(UserIn):
    senha: str


@app.get("/portal")
async def get_portal(teleport: bool = False) -> Response:
    if teleport:
        return RedirectResponse(url="https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    return JSONResponse(content={"message": "Here's your interdimensional portal."})


@app.post("/email")
async def email(email: Annotated[UserPass, Body()]) -> UserIn:
    return email


"""
@app.post("/email", response_model=UserOut)
async def email(email: Annotated[UserIn, Body()]) -> any:
 return email
"""


@app.get("/header")
async def header(header_teste: Annotated[str, Header()]):
    return {"header": header_teste}


@app.get("/cookie")
async def cookie(cookies: Annotated[int, Cookie()] = 3):
    return {"cookies": cookies}


@app.post("/tudo/{id}")
async def tudo(
    id: AnnotatedPath, post: AnnotatedBody, notificar: AnnotatedQuery = False
):
    return {"id": id, "titulo": post.titulo, "notificação": notificar}


@app.post("/post")
async def post(titulo: ModeloPost):
    return {"dicionario": f"dicionario recebido '{titulo.titulo}'"}


@app.post("/envio")
async def envio(envio: Post):

    return {
        "dados": f"titulo {envio.titulo} com conteudo {envio.conteudo} com {len(envio.comentarios or [])} comentarios recebido"
    }


@app.post("/envio/avançado")
async def envio_a(envio: Post):

    envio.titulo = envio.titulo.upper()

    return {"Dados:": envio}


@app.get("/filtro")
async def filtro(filtro_query: Annotated[Filtro, Query()]):
    return filtro_query


def check_id(id: str):
    if not id.startswith(("isbn-", "imdb-")):
        raise ValueError("Id invalido, Esperado: isbn-  imdb-")
    return id


ID = Annotated[str | None, AfterValidator(check_id)]


@app.get("/val")
async def val(id: ID | None = None):
    return {"id": id}


@app.get("/frutas")
async def frutas(fruta: FRUTAS | None = None):
    return {"fruta": fruta}


@app.get("/query")
async def query(item_id: QUERY_ID | None = None):
    return {"item_id": item_id}


@app.get("/teste/{teste}")
async def teste(teste: ITEM_ID_VALIDATION):
    return {"teste": teste}


@app.get("/items/{item_id}")
async def get_items(item_id: int):
    return {"item_id": item_id}

    #
