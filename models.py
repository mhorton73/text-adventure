
from pydantic import BaseModel, Field

STARTER_HP = 10

class Stats(BaseModel):
    
    strength: int
    dexterity: int
    intelligence: int
    faith: int

class Character(BaseModel):
    
    name: str
    rpgClass: str

    stats: Stats = Field(default_factory=Stats)
    hp: int = STARTER_HP
    max_hp: int = STARTER_HP
    gold: int = 0

    inventory: list[str] = Field(default_factory=list)
    flags: list[str] = Field(default_factory=list)
    spells: list[str] = Field(default_factory=list)

    trackers: dict[str, int] = Field(
        default_factory=dict,
        description="Flexible numeric trackers for story-specific mechanics (e.g. time, exhaustion, reputation)"
    )  

    current_node: str

