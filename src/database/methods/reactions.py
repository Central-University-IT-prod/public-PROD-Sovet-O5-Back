from database import models, db, client, methods


def create(reaction: models.Reaction):
    db.reactions.insert_one(
        reaction.model_dump(by_alias=True)
    )


def get(
    reaction: models.Reaction    
):
    reaction = db.reactions.find_one(
        reaction.model_dump(by_alias=True)
    )
    
    if reaction is None:
        return None
    
    return models.Reaction(**reaction)

def delete(
    reaction: models.Reaction    
) -> None:
    """Delete reaction by id"""
    
    db.reactions.delete_one(
        reaction.model_dump(by_alias=True)
    )


def get_join_requests(
    target_id: int
) -> list[models.UserResponse]:

    result = client.reactions.aggregate([
        {
            "$match": {
                "target_id": target_id,
                "type": models.ReactionType.join_request.value
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "object_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$project": {"user": "$user"}
        }
    ])
    
    response = []
    
    for obj in result:
        response.append(methods.users.get(obj["user"]["_id"]))
    
    return response

def get_likes(
    target_id: int
):
    result = client.reactions.aggregate([
        {
            "$match": {
                "target_id": target_id,
                "type": models.ReactionType.like.value
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "object_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$project": {"user": "$user"}
        }
    ])
    
    response = []
    
    for obj in result:
        response.append(methods.users.get(obj["user"]["_id"]))
    
    return response

def get_matches(
    target_id: int
):
    result = client.reactions.aggregate([
        {
            "$match": {
                "target_id": target_id,
                "type": models.ReactionType.match.value
            }
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "object_id",
                "foreignField": "_id",
                "as": "user"
            }
        },
        {
            "$unwind": "$user"
        },
        {
            "$project": {"user": "$user"}
        }
    ])
    
    response = []
    
    for obj in result:
        response.append(methods.users.get(obj["user"]["_id"]))
        
    return response
    