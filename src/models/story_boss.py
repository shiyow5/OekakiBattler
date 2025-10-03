"""
Story mode boss character model
"""

from pydantic import BaseModel, Field, model_validator
from typing import Optional
from datetime import datetime


class StoryBoss(BaseModel):
    """Story mode boss character"""
    level: int = Field(ge=1, le=5, description="Boss level (1-5)")
    name: str = Field(min_length=1, max_length=30)
    hp: int = Field(ge=10, le=300)
    attack: int = Field(ge=10, le=200)
    defense: int = Field(ge=10, le=150)
    speed: int = Field(ge=10, le=150)
    magic: int = Field(ge=10, le=150)
    luck: int = Field(ge=0, le=100, default=50)
    description: str
    image_path: Optional[str] = None
    sprite_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)

    @model_validator(mode='after')
    def check_total_stats(self):
        """Validate total stats do not exceed 500 for bosses"""
        total = self.hp + self.attack + self.defense + self.speed + self.magic + self.luck
        if total > 500:
            raise ValueError(f"Total boss stats ({total}) exceeds maximum allowed (500)")
        return self

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class StoryProgress(BaseModel):
    """Player's story mode progress"""
    character_id: str
    current_level: int = Field(default=1, ge=1, le=5)
    completed: bool = False
    victories: list[int] = Field(default_factory=list)  # List of defeated boss levels
    attempts: int = Field(default=0)
    last_played: datetime = Field(default_factory=datetime.now)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
