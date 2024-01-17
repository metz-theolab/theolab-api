"""Endpoints for the manipulation of manuscript data.
"""
import typing as t
import json
from fastapi import APIRouter, Depends, Request, Response
from fastapi.responses import HTMLResponse
from .models import ManuscriptAttributes


def sql_database(request: Request):
    """Access the mongo database from a Starlette/FastAPI request"""
    return request.app.state.database


router = APIRouter(
    prefix="/manuscript",
    tags=["manuscript"]
)


@router.get("/")
async def get_manuscripts(database=Depends(sql_database)):
    """List all manuscripts available.
    """
    manuscripts = await database.get_distinct_manuscripts()
    return Response(content=json.dumps({"manuscripts": manuscripts}, ensure_ascii=False).encode('utf8'),
                    media_type="application/json")



@router.get("/{manuscript_name}")
async def get_manuscript(manuscript_name: str,
                         column: t.Optional[str] = None,
                         line: t.Optional[str] = None,
                         database=Depends(sql_database)):
    """Retrieve the content of a given manuscript.
    """
    if not await database.check_manuscript_exists(manuscript_name=manuscript_name):
        error_message = "Manuscript {} not found.".format(manuscript_name)
        return Response(status_code=404, content=error_message)

    manuscript = await database.get_manuscript(manuscript_name=manuscript_name,
                                               column=column,
                                               line=line)
    if column:
        response = {manuscript_name: {column: manuscript}}
        if line:
            response = {manuscript_name: {column: {line: manuscript}}}
    else:
        response = {manuscript_name: manuscript}
    if manuscript:
        return Response(content=json.dumps(response, ensure_ascii=False).encode('utf8'),
                        media_type="application/json")
    else:
        error_message = "Manuscript {} column {} not found.".format(
            manuscript_name, column)
        if line:
            error_message = "Manuscript {} column {} line {} not found.".format(
                manuscript_name, column, line)
        return Response(status_code=404, content=error_message)


@router.get("/{manuscript_name}/display")
async def get_manuscript_display(manuscript_name: str,
                                 column: t.Optional[str] = None,
                                 line: t.Optional[str] = None,
                                 database=Depends(sql_database)):
    """Retrieve the content of a given manuscript in HTML format.
    """
    if not await database.check_manuscript_exists(manuscript_name=manuscript_name):
        error_message = "Manuscript {} not found.".format(manuscript_name)
        return Response(status_code=404, content=error_message)
    manuscript = await database.get_manuscript(manuscript_name=manuscript_name,
                                               column=column,
                                               line=line)
    if manuscript.strip():
        column_name = f"<b>{column}</b>" if column else ""
        line_name = f"<b>{line}</b>" if line else ""
        # Substitute the line breaks with HTML line breaks
        manuscript = "<body dir='rtl'>" + '<br>' + f"<b>{manuscript_name}</b><br/>" + \
            f"<b>{column_name}</b><br/>" + \
            f"<b>{line_name}</b><br/>" + \
            manuscript.replace("\n", "<br>") + "</body>"
        return HTMLResponse(manuscript)
    else:
        error_message = "Manuscript {} column {} not found.".format(
            manuscript_name, column)
        if line:
            error_message = "Manuscript {} column {} line {} not found.".format(
                manuscript_name, column, line)
        return Response(status_code=404, content=error_message)
    

@router.get("/{manuscript_name}/attributes/{attribute}")
async def get_manuscript_attributes(manuscript_name: str,
                                    attribute: ManuscriptAttributes,
                                    database=Depends(sql_database)):
    """List all columns available for a manuscript.
    """
    if not await database.check_manuscript_exists(manuscript_name=manuscript_name):
        error_message = "Manuscript {} not found.".format(manuscript_name)
        return Response(status_code=404, content=error_message)
    attributes = await database.get_manuscript_attribute(manuscript_name=manuscript_name, attribute=attribute.value)
    response = {
        manuscript_name: {attribute: attributes}
    }
    return Response(content=json.dumps(response, ensure_ascii=False).encode('utf8'),
                    media_type="application/json")

