"""Create the HTTP router to retrieve the textual tradition.
"""
import json
from typing import Optional
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from backend.api.oidc.provider import check_user
from backend.settings.settings import QWB_READ_ROLE, QWB_CLIENT_ID
from .utils import compute_letter_difference, compute_levensthein, retrieve_morphological_analysis, analyze_collations


def sql_database(request: Request):
    """Access the mongo database from a Starlette/FastAPI request"""
    return request.app.state.database


router = APIRouter(tags=["parallels"])


@router.get("/parallels/{tradition}/{chapter}/{verse}")
async def get_parallel(
    tradition: str,
    chapter: str,
    verse: str,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Retrieve all parallels associated with a tradition, a chapter and a verse."""
    result = await database.get_parallels_content(
        name=tradition, chapter=chapter, verse=verse, reconstructed=True
    )
    return Response(
        content=json.dumps(result, ensure_ascii=False).encode("utf8"),
        media_type="application/json",
    )


@router.get("/parallels/list")
async def available_parallels(
    tradition: str,
    chapter: Optional[str] = None,
    verse: Optional[str] = None,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Retrieve all parallels associated with a tradition, a chapter and a verse."""
    results = await database.get_parallels(name=tradition, chapter=chapter, verse=verse)
    return Response(
        content=json.dumps({"parallels": results}, ensure_ascii=False).encode("utf8"),
        media_type="application/json",
    )


@router.get("/parallels/{tradition}/{chapter}/{verse}/collation/html")
async def perform_collation(
    tradition: str,
    chapter: str,
    verse: str,
    reconstructed: bool,
    strip_vowels: bool,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Retrieve all parallels associated with a tradition, a chapter and a verse and perform the collation.
    If reconstructed is set to True, then the reconstructed data is held as true data."""
    collation = await database.get_html_collation(
        name=tradition, chapter=chapter, verse=verse, reconstructed=reconstructed, strip_vowels=strip_vowels
    )
    mt_text = await database.get_manuscript(manuscript_name=tradition, column=chapter, line=verse)
    html_string = (
        """
        <head>
        <meta http-equiv='Content-Type' content='text/html; charset=utf-8'>
        <title>html title</title>
        <style type='text/css' media='screen'>
        th, td {
        border-style: dotted;
        border-color: #96D4D4;
        }
        #container {
            display: flex;              
            flex-direction: column;     
            justify-content: center;    
            align-items: center; 
            height: 300px;
            border: 1px solid black;
        }
        </style>
        </head>
        <html><body>
        Collation for <b>"""
        + tradition
        + """</b> chapter <b>"""
        + chapter
        + """</b> verse <b>"""
        + verse
        + """</b><br/>
        <b>MT text</b>: <div dir="rtl">"""
        +
        mt_text
        +
        """
        </div>
        <div id="container" dir="rtl">
        """
        + collation
        + """
        </div></body></html>
        """
    )
    return HTMLResponse(content=html_string, media_type="text/html")


@router.get("/parallels/{tradition}/{chapter}/{verse}/collation/rawhtml")
async def perform_raw_collation(
    tradition: str,
    chapter: str,
    verse: str,
    reconstructed: bool,
    strip_vowels: bool,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Retrieve all parallels associated with a tradition, a chapter and a verse and perform the collation.
    If reconstructed is set to True, then the reconstructed data is held as true data."""
    html_string = await database.get_html_collation(
        name=tradition, chapter=chapter, verse=verse, reconstructed=reconstructed, strip_vowels=strip_vowels
    )
    return HTMLResponse(content=html_string, media_type="text/html")


@router.get("/parallels/{tradition}/{chapter}/{verse}/collation/analysis")
async def perform_collation_analysis(
    tradition: str,
    chapter: str,
    verse: str,
    reconstructed: bool,
    strip_vowels: bool,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Retrieve all parallels associated with a tradition, a chapter and a verse and perform the collation.
    If reconstructed is set to True, then the reconstructed data is held as true data."""
    collation = await database.get_collation(
        name=tradition, chapter=chapter, verse=verse, reconstructed=reconstructed, strip_vowels=strip_vowels
    )
    return analyze_collations(collation)


@router.get("/parallels/analysis")
async def get_variants_analysis(
    reading_1: str,
    reading_2: str,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Perform the analysis of the variants."""
    morpho_analysis_1 = await database.get_word_morphological_analysis(reading_1)
    morpho_analysis_2 = await database.get_word_morphological_analysis(reading_2)
    return {
        "levensthein": compute_levensthein(reading_1, reading_2),
        "letter_differences": compute_letter_difference(reading_1, reading_2),
        "analysis": {
            "reading_1": retrieve_morphological_analysis(morpho_analysis_1),
            "reading_2": retrieve_morphological_analysis(morpho_analysis_2),
        },
    }


@router.get("/parallels/count")
async def get_parallels_count(
    tradition: str,
    chapter: Optional[str] = None,
    database=Depends(sql_database),
    user=check_user(expected_roles=[QWB_READ_ROLE], client_id=QWB_CLIENT_ID),
):
    """Count the number of parallels for a given tradition and either a given chapter or a given verse 
    within this chapter.
    """
    result = await database.get_parallels_count(name=tradition, chapter=chapter)
    return Response(
        content=json.dumps({tradition: {
            "chapter": chapter,
            "count": result
        }}, ensure_ascii=False).encode("utf8"),
        media_type="application/json",
    )