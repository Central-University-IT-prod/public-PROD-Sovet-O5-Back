from typing import Any
import database


def insert_special_data(full_special_data: dict[str, Any]) -> None:
    
    parsed_data = database.models.FullSpecialDataScheme(
        **full_special_data
    )
    
    # insert positions
    database.client.positions.drop()
    
    for position in parsed_data.positions:
        position_to_insert = database.models.Position(
            _id=position.name,
            label=position.label
        )
        database.client.positions.insert_one(
            position_to_insert.model_dump(by_alias=True)
        )
    
    # insert special data
    database.client.specialData.drop()
    
    for special_data in parsed_data.users:
        special_data_to_insert = database.models.SpecialData(
            _id=special_data.username,
            score=special_data.score,
            position=special_data.position
        )

        database.client.specialData.insert_one(
            special_data_to_insert.model_dump(by_alias=True)
        )
        
    # insert constraints
    database.client.constraints.drop()
    
    database.methods.constraints.define_constraints(
        full_special_data.get("constraints")
    )
    
    for skill in full_special_data["skills"]:
        database.client.skills.insert_one(
            database.models.Skill(
                id=skill
            ).model_dump(by_alias=True)
        )

def get_special_data_by_username(username) -> database.models.SpecialData | None:
    
    special_data = database.client.specialData.find_one(
        {"_id": username}
    )
    
    if special_data is None:
        return None
    
    return database.models.SpecialData(**special_data)
