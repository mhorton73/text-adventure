
from pydantic import BaseModel, Field
from typing import Literal
from enum import Enum

class Stat(str, Enum):
    strength = "strength"
    dexterity = "dexterity"
    intelligence = "intelligence"
    faith = "faith"

class ComparisonOp(str, Enum):
    lt = "<"
    lte = "<="
    eq = "=="
    gte = ">="
    gt = ">"

class StoryItem(BaseModel):
    key: str
    type: Literal["item", "flag", "spell"]

class StatChange(BaseModel):
    stat: Stat
    delta: int

class NumericChange(BaseModel):
    key: str
    delta: int

class NumericCondition(BaseModel):
    key: str
    op: ComparisonOp
    value: int

# Write only
class Effect(BaseModel):
    add: list[StoryItem] = Field(default_factory=list)
    remove: list[StoryItem] = Field(default_factory=list)
    numeric_changes: list[NumericChange] = Field(default_factory=list)

# Read only
class Condition(BaseModel):
    required: list[StoryItem] = Field(default_factory=list)
    excluded: list[StoryItem] = Field(default_factory=list)
    numeric: list[NumericCondition] = Field(default_factory=list)

class SkillCheck(BaseModel):
    stat: Stat
    difficulty: int

class Choice(BaseModel):
    text: str
    condition: Condition = Field(default_factory=Condition)
    
    next_node: str | None = None
    skill_check: SkillCheck | None = None
    success_node: str | None = None
    failure_node: str | None = None

class Node(BaseModel):
    id: str
    text: str
    effects: Effect = Field(default_factory=Effect)
    choices: list[Choice]
