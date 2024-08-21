import database


def check_admin_access_by_id(user_id: int) -> bool:
    return database.client.adminsIDS.find_one(
        {"_id": user_id}
    ) is not None
    

def create_admin(user_id: int) -> None:
    admin_id = database.models.AdminId(_id=user_id)
    database.client.adminsIDS.insert_one(
        admin_id.model_dump(by_alias=True)
    )
    