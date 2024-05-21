"""Create the HTTP router to retrieve the textual tradition.
"""
from typing import Annotated, List, Literal
from pathlib import Path
import json
import anyio
from fastapi import APIRouter, File, Form, Query, Response, Request, Depends, HTTPException, WebSocket, Request, UploadFile
from loguru import logger

from .models import Content, Tradition, Manuscript
from .utils import format_readings_output

from backend.api.oidc.provider import check_user
from backend.settings.settings import SCRIBES_READ_ROLE, SCRIBES_CLIENT_ID


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
        traditions = await database.get_traditions(archived=False, user=user.preferred_username)
        if len(traditions) > 0:
            return Response(content=json.dumps(traditions, default=str,
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
                                                                archived=False,
                                                                user=user.preferred_username)
        if len(manuscripts) > 0:
            return Response(content=json.dumps(manuscripts, default=str,
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
            return Response(content=json.dumps(folios,
                                               ensure_ascii=False,  default=str).encode('utf8'),
                            media_type="application/json")
        return HTTPException(status_code=404, detail=f"No available folios within the database for manuscript {manuscript}"
                             f"of tradition {tradition}.")
    except ValueError as e:
        return HTTPException(status_code=404, detail=f"Unknown requested manuscript {manuscript} for tradition {tradition}")


@router.get("/traditions/{tradition}/{manuscript}/{folio}",
            tags=["GET"]
            )
async def get_manuscripts_folio(tradition: str,
                                manuscript: str,
                                folio: str,
                                database=Depends(sql_database),
                                user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                client_id=SCRIBES_CLIENT_ID)):
    """Get the information of a folio associated with a manuscript.
    """
    try:
        folio = await database.get_folio(tradition=tradition,
                                         manuscript=manuscript,
                                         folio=folio,
                                         user=user.preferred_username)
        if len(folio) > 0:
            return Response(content=json.dumps(folio, ensure_ascii=False, default=str).encode('utf8'), media_type="application/json")
        return Response(content=json.dumps(folio, ensure_ascii=False).encode('utf8'),
                        media_type="application/json")
    except ValueError as e:
        return HTTPException(status_code=404, detail=f"Unknown requested folio {folio} for manuscript {manuscript}"
                             f"of tradition {tradition}")


@router.get("/traditions/{tradition}/{manuscript}/{folio}/content",
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
    columns = await database.get_folio_columns(tradition=tradition,
                                               manuscript=manuscript,
                                               folio=folio,
                                               user=user.preferred_username)

    try:
        folio_content = await database.get_folio_readings(tradition=tradition,
                                                          manuscript=manuscript,
                                                          folio=folio,
                                                          user=user.preferred_username)
    except ValueError as e:
        folio_content = {"1": {"1": ""}}

    for column in columns:
        position_in_folio = column["position_in_folio"]
        if position_in_folio not in list(folio_content.keys()):
            folio_content[position_in_folio] = {"1": ""}

    try:
        folio_notes = await database.get_folio_notes(tradition=tradition,
                                                     manuscript=manuscript,
                                                     folio=folio,
                                                     user=user.preferred_username)
    except ValueError as e:
        folio_notes = {"1": {"1": ""}}

    for column in columns:
        position_in_folio = column["position_in_folio"]
        if position_in_folio not in list(folio_notes.keys()):
            folio_notes[position_in_folio] = {"1": ""}

    folio_translations = {}

    return Response(content=json.dumps({"readings": format_readings_output(folio_content),
                                        "notes": format_readings_output(folio_notes),
                                        "translations": folio_translations},
                                       ensure_ascii=False).encode('utf8'),
                    media_type="application/json")


@router.get("/traditions/{tradition}/{manuscript}/{folio}/columns",
            tags=["GET"]
            )
async def get_manuscripts_folios_columns(tradition: str,
                                         manuscript: str,
                                         folio: str,
                                         database=Depends(sql_database),
                                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                                         client_id=SCRIBES_CLIENT_ID)):
    """Retrieve all the columns associated with a folio.
    """
    try:
        columns = await database.get_folio_columns(tradition=tradition,
                                                   manuscript=manuscript,
                                                   folio=folio,
                                                   user=user.preferred_username)
        return Response(content=json.dumps(columns, ensure_ascii=False).encode('utf8'),
                        media_type="application/json")
    except ValueError as e:
        return HTTPException(status_code=404,
                             detail=f"Unknown requested folio {folio} for manuscript {manuscript}"
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


# @router.get("/traditions/collation/{tradition}/{chapter}/{verse}",
#             tags=["GET"])
# def get_manuscripts_collation(tradition: str,
#                               chapter: str,
#                               verse: str,
#                               manuscript_list: List[str] = Query(...)):
#     """Return HTML collation using collatex.

#     🚨 Easier to visualize using directly the endpoint rather than through the FastAPI.
#     """
#     # TODO : collation view
#     collation = Collation()
#     for manuscript in manuscript_list:
#         collation.add_plain_witness(
#             manuscript, TRADITION_CONTENT[tradition][manuscript][chapter][verse]["content"])
#     return Response(content=collate(collation, segmentation=False, output="xml"), media_type="application/xml")


@router.post("/{tradition}", tags=["ADD"])
async def add_tradition(tradition: str,
                        tradition_data: Tradition,
                        database=Depends(sql_database),
                        user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                        client_id=SCRIBES_CLIENT_ID)):
    """Add a textual tradition.
    """
    try:
        await database.add_tradition(
            tradition=tradition,
            note=tradition_data.note,
            is_public=tradition_data.is_public,
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
            tradition=tradition,
            username=username,
            user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add user {username} to tradition {tradition}")

    return Response(status_code=201, content=f"User {username} added to tradition {tradition}.")


@router.post("/{tradition}/{manuscript}", tags=["ADD"])
async def add_manuscript(tradition: str,
                         manuscript: str,
                         manuscript_data: Manuscript,
                         database=Depends(sql_database),
                         user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                         client_id=SCRIBES_CLIENT_ID)):
    """Add a manuscript for the selected tradition.
    """
    try:
        await database.add_manuscript(
            tradition=tradition,
            manuscript=manuscript,
            note=manuscript_data.note,
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
                    position_in_manuscript: Annotated[int, Form(...)],
                    request: Request,
                    image: UploadFile = File(None),
                    database=Depends(sql_database),
                    user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                    client_id=SCRIBES_CLIENT_ID)
                    ):
    """Add a folio for the selected manuscript.
    """
    if image:
        folio_path = str(
            request.app.state.settings.file_storage_path) + str(image.filename)
        # Store file
        with open(folio_path, "wb") as buffer:
            buffer.write(image.file.read())
    else:
        folio_path = None
    try:
        await database.add_folio(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            position_in_manuscript=position_in_manuscript,
            image_url=str(image.filename),
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add folio {folio} for manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Folio {folio} added for manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/{column}", tags=["ADD"])
async def add_column(tradition: str,
                     manuscript: str,
                     folio: str,
                     column: int,
                     database=Depends(sql_database),
                     user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                     client_id=SCRIBES_CLIENT_ID)):
    """Add a column for the selected folio.
    """
    try:
        await database.add_column(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            position_in_folio=column,
            user=user.preferred_username
        )
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to add column {column} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=201,
                    content=f"Column {column} added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


# @router.post("/{tradition}/{manuscript}/{folio}/{column}/{line}", tags=["ADD"])
# async def add_line(tradition: str,
#                    manuscript: str,
#                    folio: str,
#                    column: int,
#                    line: int,
#                    position_in_column: int,
#                    database=Depends(sql_database),
#                    user=check_user(expected_roles=[SCRIBES_READ_ROLE],
#                                    client_id=SCRIBES_CLIENT_ID)):
#     """Add a new line to a column.
#     """
#     try:
#         await database.add_line(
#             tradition=tradition,
#             manuscript=manuscript,
#             folio=folio,
#             column_position_in_folio=column,
#             position_in_column=position_in_column,
#             user=user.preferred_username
#         )
#     except ValueError as e:
#         return HTTPException(status_code=500,
#                              detail=f"Unable to add line {line} for column {column} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
#     return Response(status_code=201,
#                     content=f"Line {line} added for column {column} of folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.post("/{tradition}/{manuscript}/{folio}/content/", tags=["ADD"])
async def add_content(tradition: str,
                      manuscript: str,
                      folio: str,
                      content: Content,
                      database=Depends(sql_database),
                      user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                      client_id=SCRIBES_CLIENT_ID)):
    """Given some content, add them to the database.
    """
    # Add the readings
    folio_readings = content.readings
    for readings in folio_readings:
        try:
            # Remove existing column to overwrite
            await database.remove_column(
                tradition=tradition,
                manuscript=manuscript,
                folio=folio,
                position_in_folio=readings["column"],
                user=user.preferred_username
            )
        except ValueError as e:
            pass
        # Add column
        await database.add_column(
            tradition=tradition,
            manuscript=manuscript,
            folio=folio,
            position_in_folio=readings["column"],
            user=user.preferred_username
        )
        for ix, line in enumerate(readings["content"].split("\n")):
            try:
                # Remove existing line to overwrite
                try:
                    await database.remove_line(
                        tradition=tradition,
                        manuscript=manuscript,
                        folio=folio,
                        column_position_in_folio=readings["column"],
                        position_in_column=ix,
                        user=user.preferred_username
                    )
                except ValueError as e:
                    pass

                await database.add_line(
                    tradition=tradition,
                    manuscript=manuscript,
                    folio=folio,
                    column_position_in_folio=readings["column"],
                    position_in_column=ix,
                    user=user.preferred_username
                )
                await database.add_readings(
                    tradition=tradition,
                    manuscript=manuscript,
                    folio=folio,
                    line=ix,
                    column=readings["column"],
                    content=line,
                    user=user.preferred_username
                )
            except ValueError as e:
                return HTTPException(status_code=500,
                                     detail=f"Unable to add content for {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")

    # Add the notes
    if content.notes:
        folio_notes = content.notes
        for notes in folio_notes:
            column = notes["column"]
            for ix, line in enumerate(notes["content"].split("\n")):
                try:
                    # Remove existing line to overwrite
                    await database.remove_line_notes(
                        tradition=tradition,
                        manuscript=manuscript,
                        folio=folio,
                        column=column,
                        line=ix,
                        user=user.preferred_username
                    )
                except ValueError as e:
                    pass
                print("====")
                print("add note")
                await database.add_line_notes(
                    tradition=tradition,
                    manuscript=manuscript,
                    folio=folio,
                    column=column,
                    line=ix,
                    note=line,
                    user=user.preferred_username
                )
        return Response(status_code=201,
                        content=f"Added content for line {line} added for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


    @router.post("/{tradition}/{manuscript}/{folio}/{column}/{line}/{reading}/note", tags=["ADD"])
    async def add_note(reading: str,
                    tradition: str,
                    manuscript: str,
                    folio: str,
                    line: int,
                    column: int,
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
                column=column,
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


@router.post("/{tradition}/{manuscript}/{folio}/{column}/{line}/note", tags=["ADD"])
async def add_line_notes(tradition: str,
                         manuscript: str,
                         folio: str,
                         column: int,
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
            column=column,
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


@router.delete("/{tradition}/{manuscript}/{folio}/{column}", tags=["DELETE"])
async def delete_column(tradition: str,
                        manuscript: str,
                        folio: str,
                        column: int,
                        database=Depends(sql_database),
                        user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                        client_id=SCRIBES_CLIENT_ID)):
    """Delete a column for the selected folio.
    """
    try:
        await database.remove_column(tradition=tradition,
                                     manuscript=manuscript,
                                     folio=folio,
                                     position_in_folio=column,
                                     user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete column {column} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=200,
                    content=f"Column {column} deleted for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.delete("/{tradition}/{manuscript}/{folio}/{column}/{line}", tags=["DELETE"])
async def delete_line(tradition: str,
                      manuscript: str,
                      folio: str,
                      line: int,
                      column: int,
                      database=Depends(sql_database),
                      user=check_user(expected_roles=[SCRIBES_READ_ROLE],
                                      client_id=SCRIBES_CLIENT_ID)):
    """Delete a line for the selected folio.
    """
    try:
        await database.remove_line(tradition=tradition,
                                   manuscript=manuscript,
                                   folio=folio,
                                   column=column,
                                   line=line,
                                   user=user.preferred_username)
    except ValueError as e:
        return HTTPException(status_code=500,
                             detail=f"Unable to delete line {line} for folio {folio} of manuscript {manuscript} of tradition {tradition}")
    return Response(status_code=200,
                    content=f"Line {line} deleted for folio {folio} of manuscript {manuscript} of tradition {tradition}.")


@router.put("/{tradition}", tags=["EDIT"])
async def update_tradition_fields(tradition: str,
                                  field: Literal['is_public', 'archived', 'note'],
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
                                   field: Literal['manuscript_name', 'archived', 'note'],
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


@router.websocket("/ws/{tradition}/{manuscript}/{folio}")
async def ws(websocket: WebSocket,
             ):
    """Websocket to listen to editions on the reading table.
    """
    # Check if folio is currently being edited by other

    await websocket.accept()
    logger.info("currently connected")
    async with anyio.create_task_group() as task_group:
        async def run_edition_receiver() -> None:
            await edition_receiver(websocket=websocket, broadcaster=websocket.app.state.broadcast)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_edition_receiver)
        await edition_sender(websocket, broadcaster=websocket.app.state.broadcast)


async def edition_receiver(websocket, broadcaster):
    async for _ in websocket.iter_text():
        break
    await websocket.close()


async def edition_sender(websocket, broadcaster):
    async with broadcaster.subscribe(channel="edition") as subscriber:
        async for event in subscriber:
            logger.info(f"received a message on the edition channel {event}")
            await websocket.send_json({"message": event.message})


@router.websocket("/wsedition/{tradition}/{manuscript}/{folio}")
async def ws_editor(websocket: WebSocket,
                    ):
    """Websocket to show editions on a given line.
    """
    # Check if folio is currently being edited by other

    await websocket.accept()
    logger.info("currently connected")
    async with anyio.create_task_group() as task_group:
        async def run_edition_publisher() -> None:
            await edition_live_publisher(websocket=websocket, broadcaster=websocket.app.state.broadcast)
            task_group.cancel_scope.cancel()

        task_group.start_soon(run_edition_publisher)
        await edition_live_sender(websocket, broadcaster=websocket.app.state.broadcast)


async def edition_live_publisher(websocket, broadcaster):
    async for message in websocket.iter_text():
        logger.info("Edition message received")
        await broadcaster.publish(channel="line_edition", message=message)


async def edition_live_sender(websocket, broadcaster):
    async with broadcaster.subscribe(channel="line_edition") as subscriber:
        async for event in subscriber:
            logger.info(f"Received a message on the edition channel {event}")
            await websocket.send_json({"message": event.message})
