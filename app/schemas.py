from pydantic import BaseModel
from typing import List, Optional

class TreeAnalysisRequest(BaseModel):
    image_data: str  # base64 encoded image

class TreeCharacteristic(BaseModel):
    species: str
    trunk_rot: Optional[str] = None
    hollow: Optional[str] = None
    trunk_crack: Optional[str] = None
    trunk_damage: Optional[str] = None
    crown_damage: Optional[str] = None
    fruiting_bodies: Optional[str] = None
    dried_branches_percent: Optional[int] = None
    other_characteristics: Optional[str] = None

class TreeAnalysisResult(BaseModel):
    tree_id: int
    characteristics: TreeCharacteristic

class AnalysisResponse(BaseModel):
    results: List[TreeAnalysisResult]
    processed_image: str  # base64 encoded image with annotations
    processing_time: float
