import typing as t
from pydantic import BaseModel
from fastapi import UploadFile, File


class Content(BaseModel):
    """Content model.
    """
    content: str


class Tradition(BaseModel):
    """Tradition model.
    """
    is_public: bool
    note: str = ""


class Manuscript(BaseModel):
    """Manuscript model.
    """
    note: str = ""


