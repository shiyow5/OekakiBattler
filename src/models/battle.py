from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
import uuid

class BattleTurn(BaseModel):
    turn_number: int
    attacker_id: str
    defender_id: str
    action_type: str  # "attack", "magic", "critical", "miss"
    damage: int = 0
    is_critical: bool = False
    is_miss: bool = False
    attacker_hp_after: int
    defender_hp_after: int

class Battle(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    character1_id: str
    character2_id: str
    winner_id: Optional[str] = None
    battle_log: List[str] = Field(default_factory=list)
    turns: List[BattleTurn] = Field(default_factory=list)
    duration: float = 0.0
    created_at: datetime = Field(default_factory=datetime.now)

    # Battle statistics
    char1_final_hp: int = 0
    char2_final_hp: int = 0
    char1_damage_dealt: int = 0
    char2_damage_dealt: int = 0
    result_type: str = "Unknown"  # "KO", "Time Limit", "Draw"
    
    @property
    def is_finished(self) -> bool:
        """Check if battle is finished"""
        return self.winner_id is not None
    
    @property
    def turn_count(self) -> int:
        """Get number of turns played"""
        return len(self.turns)
    
    def add_log_entry(self, message: str):
        """Add entry to battle log"""
        self.battle_log.append(message)
    
    def add_turn(self, turn: BattleTurn):
        """Add a turn to the battle"""
        self.turns.append(turn)
        
    def to_dict(self) -> dict:
        """Convert to dictionary for database storage"""
        return {
            'id': self.id,
            'character1_id': self.character1_id,
            'character2_id': self.character2_id,
            'winner_id': self.winner_id,
            'battle_log': '|'.join(self.battle_log),  # Join with separator for storage
            'duration': self.duration,
            'created_at': self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Battle':
        """Create Battle from dictionary"""
        if isinstance(data['created_at'], str):
            data['created_at'] = datetime.fromisoformat(data['created_at'])
        if data.get('battle_log'):
            data['battle_log'] = data['battle_log'].split('|')
        else:
            data['battle_log'] = []
        return cls(**data)

class BattleResult(BaseModel):
    """Summary of battle results"""
    winner: Optional[str] = None
    total_turns: int = 0
    duration: float = 0.0
    damage_dealt: dict = Field(default_factory=dict)  # character_id -> total_damage
    critical_hits: dict = Field(default_factory=dict)  # character_id -> critical_count
    magic_used: dict = Field(default_factory=dict)    # character_id -> magic_count