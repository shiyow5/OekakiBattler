from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
import uuid

class Character(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    name: str
    hp: int = Field(ge=50, le=150)
    attack: int = Field(ge=30, le=120)
    defense: int = Field(ge=20, le=100)
    speed: int = Field(ge=40, le=130)
    magic: int = Field(ge=10, le=100)
    description: str = ""
    image_path: str
    sprite_path: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.now)
    battle_count: int = 0
    win_count: int = 0
    
    @property
    def win_rate(self) -> float:
        """Calculate win rate percentage"""
        if self.battle_count == 0:
            return 0.0
        return (self.win_count / self.battle_count) * 100
    
    @property
    def total_stats(self) -> int:
        """Calculate total stats"""
        return self.hp + self.attack + self.defense + self.speed + self.magic
    
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'name': self.name,
            'hp': self.hp,
            'attack': self.attack,
            'defense': self.defense,
            'speed': self.speed,
            'magic': self.magic,
            'description': self.description,
            'image_path': self.image_path,
            'sprite_path': self.sprite_path,
            'created_at': self.created_at.isoformat(),
            'battle_count': self.battle_count,
            'win_count': self.win_count
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Character':
        """Create Character from dictionary"""
        if isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        return cls(**data)

class CharacterStats(BaseModel):
    """Simplified model for AI stat generation"""
    name: str = Field(min_length=1, max_length=30)
    hp: int = Field(ge=50, le=150)
    attack: int = Field(ge=30, le=120)
    defense: int = Field(ge=20, le=100)
    speed: int = Field(ge=40, le=130)
    magic: int = Field(ge=10, le=100)
    description: str