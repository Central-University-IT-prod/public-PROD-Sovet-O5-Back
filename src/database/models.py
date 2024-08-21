from __future__ import annotations
import enum
from pydantic import BaseModel as PydanticBaseModel, ConfigDict, Field

class BaseModel(PydanticBaseModel):
    model_config = ConfigDict(populate_by_name=True)

class AllowedUsername(BaseModel):
    id: str = Field(alias="_id")  # allowed usename as string id

class SpecialData(BaseModel):
    id: str = Field(alias="_id")  # username
    position: str
    score: float

class Position(BaseModel):
    id: str = Field(alias="_id")  # name
    label: str

class SpecialDataScheme(BaseModel): 
    username: str
    position: str
    score: float    
    
class PositionScheme(BaseModel): 
    name: str
    label: str

class FullSpecialDataScheme(BaseModel):  
    """полное описание всех данных, которые вводят организаторы"""
    users: list[SpecialDataScheme]
    positions: list[PositionScheme]

class AdminId(BaseModel):
    id: int = Field(alias="_id")  # allowed usename as integer id

class SkillTag(BaseModel):
    lower_value: str = Field(alias="_id")
    value: str

class TeamBase(BaseModel):
    name: str
    description: str

class Team(TeamBase):
    id: int = Field(alias="_id")
    """ID для команды. Используем чит: если это неявная команда, в которой
    состоит только один пользователь, то ID команды равен ID пользователя.
    Для "полноценных" команд ID команды это автодекремент (-1, -2, etc)"""
    lead: int
    """ID лидера команды"""

class TeamResponse(TeamBase):
    id: int = Field(alias="_id")
    """ID для команды. Используем чит: если это неявная команда, в которой
    состоит только один пользователь, то ID команды равен ID пользователя.
    Для "полноценных" команд ID команды это автодекремент (-1, -2, etc)"""
    lead: UserBase
    members: list[UserBase]
    is_true: bool | None = None  # правильная ли команда

class Profile(BaseModel):
    position: str
    skills: list[str]
    description: str
    experience: str
    links: list[str]
    show_in_search: bool = True

class UserBase(BaseModel):
    """Внутренний класс"""
    id: int = Field(alias="_id")
    profile: Profile | None
    first_name: str
    last_name: str | None
    username: str
    soft_skills_match: int = 0 # КОСТЫЛЬ

class User(UserBase):
    """Внутренний класс для работы с БД"""
    rating: float
    score: float
    team_id: int
    soft_skills: list[str] = Field(default_factory=list)

class UserResponse(UserBase):
    """Класс для отображения пользователя по прямому API-запросу"""
    team: TeamResponse

class ReactionType(enum.Enum):
    like = 1
    dislike = 2
    join_request = 3
    match = 4
    service_mongo_hack = 5
    deferred = 6

class Reaction(BaseModel):
    """Модель реакции для уведомлений"""
    target_id: int
    object_id: int
    type: ReactionType | int

class ReactionResponse(BaseModel):
    user: UserResponse
    type: ReactionType | int

class TeamCreationScheme(BaseModel):
    name: str
    description: str
    members: list[int]  # list of members ids
    lead: int

class ConstraintsCommandSizeSchema(BaseModel):
    min_size: int
    max_size: int

class Constraints(BaseModel):
    command_size: ConstraintsCommandSizeSchema
    DNF: list[dict[str, int]]

class NextUserQuery(BaseModel):
    skills: list[str] | None = None
    position: str | None = None
    exclude: list[int] | None = None

class Skill(BaseModel):
    id: str = Field(alias="_id")  # skill name
