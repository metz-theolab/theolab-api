import typing as t
from pydantic import BaseModel
from fastapi import UploadFile, File


class Content(BaseModel):
    """Content model.
    """
    readings: list[dict[str, t.Union[str, int]]] = []
    notes: list[dict[str, t.Union[str, int]]] = []
    translation: list[dict[str, t.Union[str, int]]] = []

class Tradition(BaseModel):
    """Tradition model.
    """
    is_public: bool
    note: str = ""


class Manuscript(BaseModel):
    """Manuscript model.
    """
    note: str = ""


