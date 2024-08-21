from fastapi import APIRouter, Depends

from typing import Annotated, Literal

from miniapp_api.helpers import InitData, init_data_dependency, APIException
from database import models, methods


router = APIRouter()


@router.post(
    "/reactions/join_request/{object_id}/approve",
)
def approve_join_request(
    object_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):

    target_team = methods.teams.get_by_user_id(init_data.user_id)
    if target_team.lead.id != init_data.user_id:
        raise APIException(403, "YOU_ARE_NOT_LEAD_OF_TEAM")
    
    target_id = target_team.id
    
    reaction = models.Reaction(
        object_id=object_id,
        target_id=target_team.id,
        type=models.ReactionType.join_request.value
    )
    
    reaction = methods.reactions.get(
        reaction
    )
    
    if reaction is None:
        raise APIException(404, "REACTION_NOT_FOUND")
        
    if target_id > 0:  # создаем новую команду
        new_team_id = methods.teams.create(
            models.Team(
                id=0,  # изменится
                name=f"{target_id} {object_id}", #  TODO: изменить на название команды
                description="",
                lead=target_id
            )
        )
        methods.users.change_user_team(target_id, new_team_id)
        methods.users.change_user_team(object_id, new_team_id)
    else:
        methods.users.change_user_team(object_id, target_id)

    methods.reactions.delete(reaction)
    methods.reactions.delete(models.Reaction(
        object_id=object_id,
        target_id=target_id,
        type=models.ReactionType.match.value
    ))
    
    methods.reactions.delete(models.Reaction(
        object_id=target_id,
        target_id=object_id,
        type=models.ReactionType.match.value
    ))
    
    methods.reactions.create(models.Reaction(
        object_id=object_id,
        target_id=target_id,
        type=models.ReactionType.service_mongo_hack.value
    ))
    
    methods.reactions.create(models.Reaction(
        object_id=target_id,
        target_id=object_id,
        type=models.ReactionType.service_mongo_hack.value
    ))
    
    
    

@router.post(
    "/reactions/join_request/{object_id}/deny",
)
def deny_join_request(
    object_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    
    target_team = methods.teams.get_by_user_id(init_data.user_id)
    target_id = target_team.id
    
    
    if target_team.lead.id != init_data.user_id:
        raise APIException(403, "YOU_ARE_NOT_LEADER_OF_TEAM")
    
    reaction = models.Reaction(
        object_id=object_id,
        target_id=target_id,
        type=models.ReactionType.join_request.value
    )
    
    reaction = methods.reactions.get(reaction)
    
    if reaction is None:
        raise APIException(404, "REACTION_NOT_FOUND")

    
    methods.reactions.delete(reaction)


@router.get(
    "/reactions",
)
def get_reactions(
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    user_id = init_data.user_id
    
    join_requests = []
    
    user_team = methods.teams.get_by_user_id(user_id)

    if user_team.lead.id == user_id:
        join_requests = methods.reactions.get_join_requests(user_team.id)
        
    likes = methods.reactions.get_likes(user_id)
    matches = methods.reactions.get_matches(user_id)
    
    result = []
    
    for i in join_requests:
        result.append(
            models.ReactionResponse(
                user=i.model_dump(by_alias=True),
                type=models.ReactionType.join_request.value
            )
        )
    
    for i in likes:
        result.append(
            models.ReactionResponse(
                user=i.model_dump(by_alias=True),
                type=models.ReactionType.like.value
            )
        )
        
    for i in matches:
        result.append(
            models.ReactionResponse(
                user=i.model_dump(by_alias=True),
                type=models.ReactionType.match.value
            )
        )
      
    return {
        "ok": True,
        "response": result
    }
    
    
@router.post(
    "/reactions/send_join_request/{target_id}"
)
def send_join_request(
    target_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):

    target_team = methods.teams.get_by_user_id(target_id)

    methods.reactions.create(
        models.Reaction(
            target_id=target_team.id,
            object_id=init_data.user_id,
            type=models.ReactionType.join_request.value
        )
    )
    
    return {
        "ok": True
    }
