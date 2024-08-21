from typing import Annotated

from fastapi import APIRouter, Depends
from miniapp_api.helpers import InitData, SuccessfulResponse, init_data_dependency, APIException
from database import methods, models, db

router = APIRouter()


@router.get(
    "/users",
    response_model_by_alias=False
)
def get_users(_init_data: Annotated[InitData, Depends(init_data_dependency)]):
    users = methods.users.get_all()
    return users

@router.post(
    "/users/next",
    response_model_by_alias=False,
    response_model=SuccessfulResponse[list[models.UserResponse]]
)
async def get_next_user(
    filters: models.NextUserQuery,
    init_data: Annotated[InitData, Depends(init_data_dependency)],
):
    """Endpoint to get next user"""
    users = methods.users_next.next_user(
        init_data.user_id,
        position=filters.position,
        skills=filters.skills,
        exclude=filters.exclude
    )
    if users is None:
        raise APIException(404, "NO_USERS")
    
    result = []
    for user in users:
        team = methods.teams.get(user.team_id)
        result.append(
            {
                **user.model_dump(by_alias=True),
                "team": team.model_dump(by_alias=True)
            }
        )
    return {
        "ok": True,
        "response": result
    }

@router.get(
    "/users/deferred",
    response_model_by_alias=False,
    response_model=SuccessfulResponse[list[models.UserResponse]]
)
def get_deferred(
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    """Endpoint to get all users deferred by you."""
    deferred = methods.users.get_deferred(init_data.user_id)
    return {
        "ok": True,
        "response": deferred
    }

@router.get(
    "/users/{user_id}",
    response_model_by_alias=False
)
def get_user(
    user_id: int,
    _init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    """Endpoint to get user by id
    """
    if (user := methods.users.get(user_id)) is None:
        raise APIException(404, "USER_NOT_FOUND")
    return user


@router.post(
    "/users/{user_id}",
    response_model_by_alias=False
)
def update_user(
    user_id: int,
    new_profile: models.Profile,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    """Endpoint to update current user profile"""
    if (user := methods.users.get(user_id)) is None:
        raise APIException(404, "USER_NOT_FOUND")
    
    admin_id = db.adminsIDS.find_one({"_id": init_data.user_id})  # TODO: вынести в отдельный файл
    if (user_id != init_data.user_id) and (admin_id is None):
        raise APIException(403, "NOT_ALLOWED")

    methods.users.update(user.id, new_profile, insert_new=user.profile is None)
    return {
        "ok": True
    }


@router.get(
    "/users/{user_id}/get_soft_matches",
)
def get_soft_matches(
    user_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    return {
        "ok": True,
        "response": methods.users.get_soft_skills_match(init_data.user_id, user_id)
    }
    