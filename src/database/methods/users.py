from database import models, methods, users, teams, reactions

def create(user: models.User):
    methods.reactions.create(models.Reaction(
        target_id=user.id,
        object_id=user.id,
        type=models.ReactionType.service_mongo_hack.value
    ))
    users.insert_one(user.model_dump(by_alias=True))

def get(user_id: int) -> models.UserResponse:
    if (user := users.find_one({"_id": user_id})) is None:
        return None
    
    team = methods.teams.get(user["team_id"])
    if team is None:
        return None
    return models.UserResponse(**user, team=team)

def is_user_exists(user_id: int) -> bool:
    return users.find_one({"_id": user_id}) is not None
    

def get_with_username(user_id: int) -> models.User | None:
    if (user := users.find_one({"_id": user_id})) is None:
        return None
    return models.User(**user)

def get_soft_skills_match(first_user_id: int, second_user_id: int) -> int:
    first_user = models.User(**users.find_one({"_id": first_user_id}))
    second_user = models.User(**users.find_one({"_id": second_user_id}))

    result = 0
    
    for i in first_user.soft_skills:
        if i in second_user.soft_skills:
            result += 1

    return result

def get_deferred(user_id: int) -> list[models.UserResponse]:
    users_res = reactions.aggregate([
        { "$match": { 
            "type": models.ReactionType.deferred.value, 
            "object_id": user_id
        } }, 
        { "$lookup": { 
            "from": "users", 
            "localField": "target_id", 
            "foreignField": "_id", 
            "as": "user" 
        } }, 
        { "$project": { "user": 1, "_id": 0 } }, 
        { "$unwind": { "path": "$user" } }, 
        { "$lookup": { 
            "from": "teams", 
            "localField": "user.team_id", 
            "foreignField": "_id", 
            "as": "user.team" 
        } }, 
        { "$unwind": { "path": "$user.team" } }, 
        { "$lookup": { 
            "from": "users", 
            "localField": "user.team._id", 
            "foreignField": "team_id", 
            "as": "user.team.members" 
        } }, 
        { "$lookup": { 
            "from": "users", 
            "localField": "user.team.lead", 
            "foreignField": "_id", 
            "as": "user.team.lead" 
        } }, 
        { "$unwind": { "path": "$user.team.lead" } }, 
        {"$replaceRoot": {"newRoot": "$user"}}
    ])

    ret = []
    for user in users_res:
        ret.append(models.UserResponse(**user))
    return ret

def update(user_id: int, profile: models.Profile, insert_new: bool = False) -> None:
    profile_dump = profile.model_dump(by_alias=True)
    if insert_new:
        profile_dump["show_in_search"] = True
        users.update_one(
            {"_id": user_id},
            {"$set": {"profile": profile_dump}}
        )
    else:
        to_update = {f"profile.{k}": v for k, v in profile_dump.items()}
        users.update_one(
            {"_id": user_id},
            {"$set": to_update}
        )

def change_user_team(user_id: int, new_team_id: int) -> None:
    prev_team = methods.teams.get_by_user_id(user_id)

    if prev_team.lead.id == user_id and len(prev_team.members) > 2:
        index = 0
        while prev_team.members[index].id == user_id:
            index += 1
        new_lead = prev_team.members[index].id
        teams.update_one(
            {"_id": prev_team.id},
            {"$set": {"lead": new_lead}}
        )
    elif len(prev_team.members) == 2:
        teams.delete_one(
            {"_id": prev_team.id}
        )
        index = 0
        while prev_team.members[index].id == user_id:
            index += 1
            
        users.update_one(   
            {"_id": prev_team.members[index].id},
            {"$set": {"team_id": prev_team.members[index].id}}
        )
    
    users.update_one(
        {"_id": user_id},
        {"$set": {"team_id": new_team_id}}
    )

def set_soft_skills(user_id: int, soft_skills: list[str]) -> None:
    users.update_one(
        {"_id": user_id},
        {"$set": {"soft_skills": soft_skills}}
    )

def get_all() -> list[models.User]:
    result = users.find({})
    response = []
    for user in result:
        response.append(models.User(**user))
        
    return response
