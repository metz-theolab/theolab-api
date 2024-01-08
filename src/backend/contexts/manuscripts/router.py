"""Endpoints for the manipulation of manuscript data.
"""

from fastapi import APIRouter


router = APIRouter(
    tags=["manuscript"]
)


@router.get("/manuscript/{name}")
def get_manuscript(name: str):
    """Retrieve the content of a given manuscript.
    """
    return {"manuscript_A": "content"}