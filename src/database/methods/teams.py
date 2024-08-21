import database
from database import db, methods


def create_individual(team: database.models.Team) -> None:    
    database.client.teams.insert_one(
        team.model_dump(by_alias=True)
    )

def create(team: database.models.Team) -> int:
    return database.client.insert_one_with_id(
        database.client.teams,
        team.model_dump(by_alias=True),
        inc_value=-1
    )

def delete(team_id: int) -> None:
    database.client.teams.delete_one(
        {"_id": team_id}
    )

def get(team_id: int) -> database.models.TeamResponse | None:
    team = list(db.teams.aggregate([
        {
            "$match": {
                "_id": team_id
            }
        },
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "team_id",
            "as": "members"
        }},
        {"$lookup": {
            "from": "users",
            "localField": "lead",
            "foreignField": "_id",
            "as": "lead"
        }},
        {"$unwind": "$lead"}
    ]))
    if not team:
        return None
    
    resp = database.models.TeamResponse(**team[0], is_true=True)
    is_true = methods.constraints.is_team_true(resp.members)
    resp.is_true = is_true
    return resp

def get_all() -> list[database.models.TeamResponse] | None:
    teams = list(db.teams.aggregate([
        {"$lookup": {
            "from": "users",
            "localField": "_id",
            "foreignField": "team_id",
            "as": "members"
        }},
        {"$lookup": {
            "from": "users",
            "localField": "lead",
            "foreignField": "_id",
            "as": "lead"
        }},
        {"$unwind": "$lead"}
    ]))
    if not teams:
        return None
    
    return [database.models.TeamResponse(**team, is_true=methods.constraints.is_team_true([database.models.UserBase(**i) for i in team["members"]])) for team in teams]
    
def get_by_user_id(user_id: int) -> database.models.TeamResponse:  # TODO: возвращать None если пользователь не в команде
    target_team_id = db.users.find_one({"_id": user_id})["team_id"]
    return get(target_team_id)

def change_lead(team_id: int, user_id: int) -> None:
    database.client.teams.update_one({"_id": team_id}, {"$set": {"lead": user_id}})