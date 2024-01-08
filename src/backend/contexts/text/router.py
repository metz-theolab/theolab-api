"""Create the HTTP router to retrieve the textual tradition.
"""

from fastapi import APIRouter


router = APIRouter(
    tags=["text"]
)


@router.get("/tradition/{name}")
def get_tradition(name: str, chapter: str, verse: str):
    """Retrieve all textual traditions associated with a tradition name.
    """
    return {"text_A": "content"}
