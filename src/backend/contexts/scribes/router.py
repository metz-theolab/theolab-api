"""Create the HTTP router to retrieve the textual tradition.
"""
from typing import List, Literal, Optional
import json
from fastapi import APIRouter, Query, Response, Request, Depends, HTTPException
from .db import ALL_TRADITIONS, MANUSCRIPTS_PER_TRADITION, FOLIOS_PER_MANUSCRIPT, FOLIO_CONTENT, TRADITION_CONTENT
from backend.api.oidc.provider import check_user
from backend.settings.settings import SCRIBES_READ_ROLE, SCRIBES_CLIENT_ID

from collatex import collate, Collation


# TODO: factorize the database access
def sql_database(request: Request):
    """Access the mongo database from a Starlette/FastAPI request"""
    return request.app.state.database


router = APIRouter(
    tags=["scribes"]
)


@router.get("/traditions",
            tags=["GET"])
async def get_traditions(database=Depends(sql_database),
                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                         client_id=SCRIBES_CLIENT_ID)):
    """Retrieve all existing textual traditions within the application.
    """
    try:
        traditions = await database.get_traditions(archived=0, user=user.preferred_username)
        if len(traditions) > 0:
            return Response(content=json.dumps({"traditions": traditions},
                                               ensure_ascii=False).encode('utf8'),
                            media_type="application/json")
        return HTTPException(status_code=404, detail=f"No available traditions within the database.")
    except ValueError:
        return HTTPException(status_code=404, detail=f"No available traditions within the database.")


@router.get("/traditions/{tradition}",
            tags=["GET"])
async def get_manuscripts(tradition: str,
                          database=Depends(sql_database),
                          user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                          client_id=SCRIBES_CLIENT_ID)):
    """Retrieve all manuscripts associated with a tradition.
    """
    try:
        manuscripts = await database.get_traditions_manuscripts(tradition,
                                                                archived=0,
                                                                user=user.preferred_username)
        if len(manuscripts) > 0:
            return Response(content=json.dumps({"manuscripts": manuscripts},
                                               ensure_ascii=False).encode('utf8'),
                            media_type="application/json")
        return HTTPException(status_code=404, detail=f"No available manuscripts within the database for tradition {tradition}.")
    except ValueError as e:
        return Response(status_code=404, content=f"Unknown requested tradition {tradition}")


@router.get("/traditions/{tradition}/{manuscript}",
            tags=["GET"])
async def get_manuscripts_folios(tradition: str,
                                 manuscript: str,
                                 database=Depends(sql_database),
                                 user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                 client_id=SCRIBES_CLIENT_ID)):
    """Retrieve all folios associated with a manuscript and their corresponding image path.
    """
    try:
        folios = await database.get_manuscripts_folios(tradition, manuscript, user=user.preferred_username)
        if len(folios) > 0:
            return Response(content=json.dumps({"folios": folios},
                                               ensure_ascii=False).encode('utf8'),
                            media_type="application/json")
        return HTTPException(status_code=404, detail=f"No available folios within the database for manuscript {manuscript}"
                             "of tradition {tradition}.")
    except ValueError as e:
        return HTTPException(status_code=404, detail=f"Unknown requested manuscript {manuscript} for tradition {tradition}")


@router.get("/traditions/{tradition}/{manuscript}/{folio}",
            tags=["GET"]
            )
async def get_manuscripts_folios_content(tradition: str,
                                         manuscript: str,
                                         folio: str,
                                         database=Depends(sql_database),
                                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                         client_id=SCRIBES_CLIENT_ID)):
    """Retrieve all the content associated with a folio:
        - The translation; #TODO still waiting for the translation
        - The page of the image;
        - The textual content
    """
    try:
        folio_content = await database.get_folio_readings(tradition=tradition,
                                                          manuscript=manuscript,
                                                          folio=folio,
                                                          user=user.preferred_username)
        return Response(content=json.dumps(folio_content, ensure_ascii=False).encode('utf8'),
                        media_type="application/json")
    except ValueError as e:
        return HTTPException(status_code=404, detail=f"Unknown requested folio {folio} for manuscript {manuscript}"
                             f"of tradition {tradition}")


@router.get("/traditions/synoptic/{tradition}/{chapter}/{verse}",
            tags=["GET"])
def get_manuscripts_synoptic(tradition: str,
                             chapter: str,
                             verse: str,
                             manuscript_list: List[str] = Query(...)):
    """Retrieve content matching the chapter and the verse for a given
    manuscript list.
    """
    # TODO: synoptic view


@router.get("/traditions/collation/{tradition}/{chapter}/{verse}",
            tags=["GET"])
def get_manuscripts_collation(tradition: str,
                              chapter: str,
                              verse: str,
                              manuscript_list: List[str] = Query(...)):
    """Return HTML collation using collatex.

    🚨 Easier to visualize using directly the endpoint rather than through the FastAPI.
    """
    # TODO : collation view
    collation = Collation()
    for manuscript in manuscript_list:
        collation.add_plain_witness(
            manuscript, TRADITION_CONTENT[tradition][manuscript][chapter][verse]["content"])
    return Response(content=collate(collation, segmentation=False, output="xml"), media_type="application/xml")


@router.post("/{tradition}", tags=["ADD"])
async def add_tradition(tradition: str,
                        is_public: bool,
                        note: Optional[str] = "",
                        database=Depends(sql_database),
                        user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                        client_id=SCRIBES_CLIENT_ID)):
    """Add a textual tradition.
    """
    try:
        await database.add_tradition(
            tradition=tradition,
            note=note,
            is_public=is_public,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add tradition {tradition}")

    return Response(status_code=201, content=f"Tradition {tradition} added.")


@router.post("/permissions/{tradition}/{username}", tags=["ADD"])
async def add_permissions(tradition: str,
                          username: str,
                          database=Depends(sql_database),
                          user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                          client_id=SCRIBES_CLIENT_ID)):
    """Add a user to the permissions list of the tradition.
    """
    try:
        await database.add_user_tradition(
                        tradition = tradition,
                        username = username,
                        user = user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add user {username} to tradition {tradition}")

    return Response(status_code=201, content=f"User {username} added to tradition {tradition}.")


@router.post("/{tradition}/{manuscript}", tags=["ADD"])
async def add_manuscript(tradition: str,
                         manuscript: str,
                         note: Optional[str] = "",
                         database=Depends(sql_database),
                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                         client_id=SCRIBES_CLIENT_ID)):
    """Add a manuscript for the selected tradition.
    """
    try:
        await database.add_manuscript(
            tradition=tradition,
            manuscript=manuscript,
            note=note,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add manuscript {manuscript} for tradition {tradition}")
    return Response(status_code=201,
                    content=f"Manuscript {manuscript} added for tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}", tags=["ADD"])
async def add_folio(tradition: str,
                    manuscript: str,
                    folio: str,
                    position_in_manuscript: int,
                    database=Depends(sql_database),
                    user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                    client_id=SCRIBES_CLIENT_ID)):
    """Add a folio for the selected manuscript.
    """
    try:
        await database.add_folio(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            position_in_manuscript=position_in_manuscript,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add folio {folio} for manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Folio {folio} added for manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/{line}", tags=["ADD"])
async def add_line(tradition: str,
                   manuscript: str,
                   folio: str,
                   line: int,
                   database=Depends(sql_database),
                   user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                   client_id=SCRIBES_CLIENT_ID)):
    """Add a line for the selected folio.
    """
    try:
        await database.add_line(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            line_number=line,
            position_in_folio=line,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add line {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Line {line} added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/{line}/", tags=["ADD"])
async def add_readings(tradition: str,
                       manuscript: str,
                       folio: str,
                       line: int,
                       content: str,
                       database=Depends(sql_database),
                       user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                       client_id=SCRIBES_CLIENT_ID)):
    """Add a line for the selected folio.
    """
    try:
        # Remove existing line to overwrite
        await database.remove_line(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            line=line,
            user=user.preferred_username
        )
        # Add new empty line
        await database.add_line(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            line_number=line,
            position_in_folio=line,
            user=user.preferred_username
        )
    except ValueError as e:
        pass
    try:
        await database.add_readings(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            line=line,
            content=content,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add content for {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Added content for line {line} added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/{line}/{reading}/note", tags=["ADD"])
async def add_note(reading: str,
                   tradition: str,
                   manuscript: str,
                   folio: str,
                   line: int,
                   position_in_line: int,
                   note: str,
                   category: str = Query(
                       "readings", enum=["reading", "translation"]),
                   database=Depends(sql_database),
                   user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                   client_id=SCRIBES_CLIENT_ID)):
    """Add a note for a given reading.
    """
    try:
        await database.add_reading_notes(
            reading=reading,
            note=note,
            tradition=tradition,
            manuscript=manuscript,
            line=line,
            folio=folio,
            category=category,
            position_in_line=position_in_line,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add note for reading {reading} "
                             "line {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Note added for reading {reading} for line {line}"
                    f" added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/{line}/note", tags=["ADD"])
async def add_line_notes(tradition: str,
                         manuscript: str,
                         folio: str,
                         line: int,
                         note: str,
                         database=Depends(sql_database),
                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                         client_id=SCRIBES_CLIENT_ID)):
    """Add a note for the selected line.
    """
    try:
        await database.add_line_notes(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            line=line,
            note=note,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add note for line {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Note added for line {line} added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.delete("/{tradition}", tags=["DELETE"])
async def delete_tradition(tradition: str,
                           database=Depends(sql_database),
                           user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                           client_id=SCRIBES_CLIENT_ID)):
    """Delete a textual tradition.
    """
    try:
        await database.remove_tradition(tradition=tradition,
                                        user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete tradition {tradition}")
    return Response(status_code=200,
                    content=f"Tradition {tradition} deleted.")


@router.delete("/{tradition}/{manuscript}", tags=["DELETE"])
async def delete_manuscript(tradition: str,
                            manuscript: str,
                            database=Depends(sql_database),
                            user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                            client_id=SCRIBES_CLIENT_ID)):
    """Delete a manuscript for the selected tradition.
    """
    try:
        await database.remove_manuscript(tradition=tradition,
                                         manuscript=manuscript,
                                         user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete manuscript {manuscript} for tradition {tradition}")
    return Response(status_code=200,
                    content=f"Manuscript {manuscript} deleted for tradition {tradition}.")


@router.delete("/{tradition}/{manuscript}/{folio}", tags=["DELETE"])
async def delete_folio(tradition: str,
                       manuscript: str,
                       folio: str,
                       database=Depends(sql_database),
                       user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                       client_id=SCRIBES_CLIENT_ID)):
    """Delete a folio for the selected manuscript.
    """
    try:
        await database.remove_folio(tradition=tradition,
                                    manuscript=manuscript,
                                    folio=folio,
                                    user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete folio {folio} for manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=200,
                    content=f"Folio {folio} deleted for manuscript {manuscript} of tradition {tradition}.")


@router.delete("/{tradition}/{manuscript}/{folio}/{line}", tags=["DELETE"])
async def delete_line(tradition: str,
                      manuscript: str,
                      folio: str,
                      line: int,
                      database=Depends(sql_database),
                      user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                      client_id=SCRIBES_CLIENT_ID)):
    """Delete a line for the selected folio.
    """
    try:
        await database.remove_line(tradition=tradition,
                                   manuscript=manuscript,
                                   folio=folio,
                                   line=line,
                                   user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete line {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=200,
                    content=f"Line {line} deleted for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.put("/{tradition}", tags=["EDIT"])
async def update_tradition_fields(tradition: str,
                                  field: Literal['is_public','archived','note'],
                                  value: str,
                                  database=Depends(sql_database),
                                  user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                  client_id=SCRIBES_CLIENT_ID)):
    """Update a textual tradition.
    """
    try:
        await database.update_tradition(tradition=tradition,
                                        field=field,
                                        value=value,
                                        user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to update tradition {tradition}")


@router.put("/{tradition}/{manuscript}", tags=["EDIT"])
async def update_manuscript_fields(tradition: str,
                                   manuscript: str,
                                   field: Literal['manuscript_name','archived','note'],
                                   value: str,
                                   database=Depends(sql_database),
                                   user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                   client_id=SCRIBES_CLIENT_ID)):
    """Update a textual tradition.
    """
    try:
        await database.update_manuscript(tradition=tradition,
                                         manuscript=manuscript,
                                         field=field,
                                         value=value,
                                         user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to update tradition {tradition}")
