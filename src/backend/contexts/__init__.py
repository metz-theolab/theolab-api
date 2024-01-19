from fastapi import Request
from .manuscripts.router import router as manuscript_router
from .text.router import router as text_router
from .morphological_analysis.router import router as morphological_analysis_router
from .manuscripts.db import ManuscriptClient
from .morphological_analysis.db import MorphologicalAnalysisClient

ROUTERS = [manuscript_router, text_router, morphological_analysis_router]


class APISQLClient(ManuscriptClient, MorphologicalAnalysisClient):
    """Create MixIn of all databases.
    """


