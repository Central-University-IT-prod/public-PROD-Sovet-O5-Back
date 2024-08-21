from fastapi import APIRouter, Depends

from typing import Annotated

from miniapp_api.helpers import InitData, init_data_dependency, APIException
from database import methods, models, db

router = APIRouter()

@router.get(
    "/teams/my",
    response_model_by_alias=False
)
def my_team(
    init_data: Annotated[InitData, Depends(init_data_dependency)]
) :
    """
    Get my team
    if user has no team, return None
    """
    
    team = methods.teams.get_by_user_id(init_data.user_id)
    
    if len(team.members) == 1:  # if user has no team, return None
        team = None
    
    return {
        "ok": True,
        "response": team        
    }
    
@router.get(
    "/teams/{user_id}",
    response_model_by_alias=False
)
def get_team_by_user_id(
    user_id: int,
    _init_data: Annotated[InitData, Depends(init_data_dependency)]  # TODO: set auth
):
    """
    Get team by user id
    if user has no team, return None
    """
    
    team = methods.teams.get_by_user_id(user_id)
    
    if len(team.members) == 1:  # if user has no team, return None
        team = None
        
    return {
        "ok": True,
        "response": team
    }


@router.post(
    "/teams/my/{user_id}/remove",
)
def remove_user_from_my_team(
    user_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    team = methods.teams.get_by_user_id(init_data.user_id)
    
    if team.lead.id != init_data.user_id:
        raise APIException(403, "YOU_ARE_NOT_LEADER_OF_TEAM")
    
    has_team_member = False
    
    for member in team.members:
        if member.id == user_id:
            has_team_member = True
            break
        
    if not has_team_member:
        raise APIException(404, "USER_NOT_IN_TEAM")
    
    methods.users.change_user_team(user_id, user_id)

    return {
        "ok": True
    }


@router.post(
    "/teams/my/{user_id}/change_lead"
)
def change_lead(
    user_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    team = methods.teams.get_by_user_id(init_data.user_id)
    
    if team.lead.id != init_data.user_id:
        raise APIException(403, "YOU_ARE_NOT_LEADER_OF_TEAM")
    
    has_team_member = False
    
    for member in team.members:
        if member.id == user_id:
            has_team_member = True
            break
        
    if not has_team_member:
        raise APIException(404, "USER_NOT_IN_TEAM")
    
    methods.teams.change_lead(team.id, user_id)

    return {
        "ok": True
    }

@router.post("/teams/quit")
def quit_team(
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    methods.users.change_user_team(init_data.user_id, init_data.user_id)
    return {"ok": True}


@router.post(
    "/teams/my/change_name/{name}",
)
def change_name(
    name: str,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    
    team = methods.teams.get_by_user_id(init_data.user_id)
    
    if team.lead.id != init_data.user_id:
        raise APIException(403, "YOU_ARE_NOT_LEADER_OF_TEAM")
    
    
    db.teams.update_one(
        {"_id": team.id},
        {
            "$set": {
                "name": name,
            }
        }
    )
    
    return {
        "ok": True
    }