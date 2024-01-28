"""Create the HTTP router to retrieve the textual tradition.
"""
import json
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from backend.api.oidc.provider import check_user
from backend.settings.settings import QWB_READ_ROLE, QWB_CLIENT_ID


def sql_database(request: Request):
    """Access the mongo database from a Starlette/FastAPI request"""
    return request.app.state.database


router = APIRouter(
    tags=["parallels"]
)


@router.get("/parallels/{tradition}/{chapter}/{verse}")
async def get_parallel(tradition: str, chapter: str, verse: str,
                       database=Depends(sql_database),
                       user=check_user(expected_roles=[QWB_READ_ROLE],
                                       client_id=QWB_CLIENT_ID)):
    """Retrieve all parallels associated with a tradition, a chapter and a verse.
    """
    result = await database.get_parallels_content(name=tradition,
                                                  chapter=chapter,
                                                  verse=verse)
    return Response(content=json.dumps(result, ensure_ascii=False).encode('utf8'),
                    media_type="application/json")


@router.get("/parallels/{tradition}/{chapter}/{verse}/list")
async def available_parallels(tradition: str, chapter: str, verse: str,
                              database=Depends(sql_database),
                              user=check_user(expected_roles=[QWB_READ_ROLE],
                                              client_id=QWB_CLIENT_ID)):
    """Retrieve all parallels associated with a tradition, a chapter and a verse.
    """
    results = await database.get_parallels(name=tradition,
                                                   chapter=chapter,
                                                   verse=verse)
    return Response(content={"parallels": json.dumps(results, ensure_ascii=False).encode('utf8')},
                    media_type="application/json")


@router.get("/parallels/{tradition}/{chapter}/{verse}/collation")
async def perform_collation(tradition: str, chapter: str, verse: str,
                      database=Depends(sql_database),
                      user=check_user(expected_roles=[QWB_READ_ROLE],
                                      client_id=QWB_CLIENT_ID)):
    """Retrieve all parallels associated with a tradition, a chapter and a verse and perform the collation.
    """
    collation = await database.get_html_collation(name=tradition,
                                                  chapter=chapter,
                                                  verse=verse)
    html_string = """
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
        Collation for <b>""" + tradition + """</b> chapter <b>""" + chapter + """</b> verse <b>""" + verse + """</b>
        <div id="container" dir="rtl">
        """ + collation + \
        """
        </div></body></html>
        """
    return HTMLResponse(content=html_string,
                        media_type="text/html")
