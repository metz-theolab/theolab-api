"""Endpoints to retrieve the lexicometirc analysis of words found within the QWB database.
"""
import typing as t
import json
from fastapi import APIRouter, Request, Depends, Response
from backend.api.oidc.provider import check_user
from backend.settings.settings import QWB_READ_ROLE, QWB_CLIENT_ID

def sql_database(request: Request):
    """Access the mongo database from a Starlette/FastAPI request"""
    return request.app.state.database


router = APIRouter(
    prefix="/lexicometric",
    tags=["Lexicometric Analysis"]
)


@router.get("/{word}")
async def get_word_analysis(word: str,
                            manuscript: t.Optional[str] = None,
                            column: t.Optional[str] = None,
                            line: t.Optional[str] = None,
                            database=Depends(sql_database),
                            user=check_user(expected_roles=[QWB_READ_ROLE],
                                            client_id=QWB_CLIENT_ID)):
    """Given a word, list all lexicometric analysis available for this word.
    Optionally, can be filtered by manuscript, column and line.
    If manuscript is not filled out, column and line are ignored.
    If column is not filled out, line is ignored.
    """
    word_analysis = await database.get_word_morphological_analysis(word=word,
                                                                   manuscript=manuscript,
                                                                   column=column,
                                                                   line=line)
    if not word_analysis:
        return Response(status_code=404, content=f"No morphological analysis for word {word} at "
                        "the provided location.")
    return Response(content=json.dumps({word: word_analysis},
                    ensure_ascii=False).encode('utf8'),
                    media_type="application/json")
