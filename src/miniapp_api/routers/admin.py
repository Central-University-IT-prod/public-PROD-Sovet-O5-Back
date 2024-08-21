from fastapi import APIRouter, Depends

from typing import Annotated, Literal

from miniapp_api.helpers import InitData, init_data_dependency, APIException
from database import models, methods


router = APIRouter()



@router.get(
    "/admin/get_teams"
)
def get_commands(
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    
    is_admin = methods.admins_ids.check_admin_access_by_id(init_data.user_id)
    
    if not is_admin:
        raise APIException(403, "YOU_ARE_NOT_ADMIN")
    
    
    teams = methods.teams.get_all()
    
    return {
        "ok": True,
        "response": teams
    }


@router.post(
    "/admin/remove_team/{team_id}"
)
def remove_team(
    team_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    is_admin = methods.admins_ids.check_admin_access_by_id(init_data.user_id)
    
    if not is_admin:
        raise APIException(403, "YOU_ARE_NOT_ADMIN")
    
    
    team = methods.teams.get(team_id)
    
    members = team.members
    
    for member in members:
        methods.users.change_user_team(member.id, member.id)
    
    methods.teams.delete(team_id)

    return {
        "ok": True
    }


@router.post(
    "/admin/move_user/{user_id}/{target_team_id}"
)
def move_user(
    user_id: int,
    target_team_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    is_admin = methods.admins_ids.check_admin_access_by_id(init_data.user_id)
    
    if not is_admin:
        raise APIException(403, "YOU_ARE_NOT_ADMIN")
    
    methods.users.change_user_team(user_id, target_team_id)

    return {
        "ok": True
    }


@router.post(
    "/admin/create_team"
)
def create_team(
    team_to_create: models.TeamCreationScheme,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    
    is_admin = methods.admins_ids.check_admin_access_by_id(init_data.user_id)

    if not is_admin:
        raise APIException(403, "YOU_ARE_NOT_ADMIN")
    
    
    team = models.Team(
        id=0, # auto-decrement
        lead=team_to_create.lead,
        name=team_to_create.name,
        description=team_to_create.description
    )
    
    new_team_id = methods.teams.create(team)
    
    team_to_create.members = list(set(team_to_create.members))
    
    for member_id in team_to_create.members:
        methods.users.change_user_team(member_id, new_team_id)
        
    return {
        "ok": True
    }
    