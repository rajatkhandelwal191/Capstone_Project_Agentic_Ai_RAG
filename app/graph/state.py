from pydantic import BaseModel
from typing import Optional, Dict, Any


class GraphState(BaseModel):
    user_input: str
    request_id: Optional[str] = None
    intent: Optional[str] = None
    response: Optional[str] = None

    uploaded_file: Optional[str] = None
    needs_upload: bool = False
