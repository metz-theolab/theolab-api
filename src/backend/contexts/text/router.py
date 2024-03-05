"""Create the HTTP router to retrieve the textual tradition.
"""

from fastapi import APIRouter


router = APIRouter(
    tags=["text"]
)


@router.get("/tradition/{name}")
def get_tradition(name: str, chapter: str, verse: str):
    """Retrieve all textual traditions associated with a tradition name.
    
    FOR NOW, this endpoint is limited to biblical data, but will soon be extended to other
    traditions found at Qumran.
    """
    return {"text_A": "content"}
