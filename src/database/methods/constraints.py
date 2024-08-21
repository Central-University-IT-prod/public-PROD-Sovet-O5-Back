from typing import Literal

import database


def define_constraints(
    constraints_to_define: dict
):
    constraints = database.models.Constraints(**constraints_to_define)
    
    database.client.constraints.insert_one(
        constraints.model_dump(by_alias=True)
    )


def get_constraints() -> database.models.Constraints | None:
    data = database.client.constraints.find_one({})
    return database.models.Constraints(**data)

def can_team_invite(
    team_members_size: int
) -> bool:
    "Может ли команда добавлять к себе пользователей"
    
    constraints = get_constraints()
    if team_members_size >= constraints.command_size.max_size:
        return False
    return True


def is_team_true(
    team_members: list[database.models.UserBase]
):
    constraints = get_constraints()
    
    if not (constraints.command_size.min_size <= len(team_members) <= constraints.command_size.max_size):
        return False

    DNF = constraints.DNF
    
    for conjuction in DNF:
        for member in team_members:
            if member.profile is None:
                continue
            if member.profile.position in conjuction:
                conjuction[member.profile.position] -= 1

        is_valid = True
        for value in conjuction.values():
            if value > 0:
                is_valid = False
        
        if is_valid:
            return True
        
    return False
    