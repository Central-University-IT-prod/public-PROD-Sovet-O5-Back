"""Методы для получения следующего пользователя для рекомендаций"""
from database import models, reactions, methods
import numpy as np
import statistics


def next_user(
        user_id: int, 
        position: str | None = None, 
        skills: list[str] | None = None,
        exclude: list[int] | None = None
) -> list[models.User] | None:
    """Возврат пользователя для рекомендаций для текущего user_id"""
    
    query = []
    
    if position is not None:
        query.append(
            {
                "$match": {
                    "users.profile.position": position
                }
            }
        )
    
    if skills is not None:
        query.append(
            {
                "$match": {
                    "users.profile.skills": {
                        "$all": skills
                    }
                }
            }
        )
    
    if exclude is not None:
        query.append(
            {
                "$match": {
                    "users._id": {
                        "$nin": exclude
                    }
                }
            }
        )
    
    res = list(reactions.aggregate([
        {
            "$match": {"object_id": user_id}
        },
        {
            "$lookup": {
                "from": "users",
                "localField": "target_id",
                "foreignField": "_id",
                "as": "excluded_users"
            }
        },
        {"$unwind": "$excluded_users"},
        {
            "$project": {
                "user": "$excluded_users._id",
                "_id": 0
            }
        },
        {
            "$group": {
                "_id": "$_id",
                "reacted_user_ids": {
                    "$push": "$user"
                }
            }
        },
        {
            "$lookup": {
                "from": "users",
                "let": {
                    "reacted_user_ids": "$reacted_user_ids"
                },
                "pipeline": [{
                    "$match": {
                        "$expr": {
                            "$and": [
                                {
                                    "$not": {
                                        "$in": ["$_id", "$$reacted_user_ids"]
                                    }
                                },
                                {
                                    "$ne": ["$_id", user_id]
                                }
                            ]
                        },
                    }
                }],
                "as": "users"
            },
        },
        {"$unwind": "$users"},
        {"$replaceRoot": {"newRoot": "$users"}},
        {
            "$group": {
                "_id": None,
                "users": { "$push": "$$ROOT" }
            }
        },
        {
            "$lookup": {
                "from": "users",
                "as": "me",
                "pipeline": [
                    {
                        "$match": {
                            "_id": user_id
                        }
                    }
                ]
            }
        },
        {
            "$addFields": {"exclude_my_team_id": "$me.team_id"}
        },
        {"$unwind": "$exclude_my_team_id"},
        {
            "$project": {
                "_id": 0,
                "users": {
                    "$filter": {
                        "input": "$users",
                        "as": "user",
                        "cond": {
                            "$ne": ["$$user.team_id", "$exclude_my_team_id"]
                        }
                    }
                }
            }
        },
        {"$unwind": "$users"},
        {"$match": {
            "users.profile": {"$ne": None},
            "users.profile.show_in_search": {"$ne": False}
        }},
        *query,
        # {"$sample": {"size": 3}}
    ]))


    if not res:
        print("150")
        return None
    
    # if res:
    #     result = []
    #     for user in res:
    #         result.append(models.User(**user["users"]))
    #     return result
    all_users = methods.users.get_all()
    median_score = statistics.median([user.score for user in all_users])
    exists_users_with_rating_large_than_median = False


    def softmax(x):
        """Compute softmax values for each sets of scores in x."""
        e_x = np.exp(x - np.max(x))
        return e_x / e_x.sum()

    # max_rating = 0
    # min_rating = 1000000000000000

    for user_raw in res:
        user = user_raw["users"]
        if user["rating"] > median_score:
            exists_users_with_rating_large_than_median = True
        
    weights_raw = [
        user["users"]["rating"] for user in res
    ]  # можно возвести в степень чтобы увеличить / уменьшить влияние на вероятность разности разброса
    if exists_users_with_rating_large_than_median:
        weights = softmax(weights_raw)
        
        max_population = len(res)
        to_return = list(np.random.choice(res, min(1, max_population), replace=False, p=weights))
        if len(to_return) == 0:
            print(184)
            return None
        
        ooo = []
        for user in to_return:
            ur = models.User(**user["users"])
            ur.soft_skills_match=methods.users.get_soft_skills_match(user_id, user["users"]["_id"])
            ooo.append(ur)
        return ooo

    weights_pre = list(softmax(weights_raw))
    
    alpha = 0.25  # влияние софт скиллов на итоговый вес
    
    soft_skills_raw = [
        methods.users.get_soft_skills_match(user_id, user["users"]["_id"]) for user in res
    ]
    
    weights = []
    
    if sum(soft_skills_raw) == 0:
        weights = weights_pre
    else:
        soft_skills = list(softmax(soft_skills_raw))

        weights = [
            soft_skills[i] * alpha + weights_pre[i] * (1 - alpha) for i in range(len(res))
        ]
    
    max_population = len(res)
    to_return = list(np.random.choice(res, min(1, max_population), replace=False, p=weights))
    if len(to_return) == 0:
        print('209')
        return None
    ooo = []
    for user in to_return:
        ur = models.User(**user["users"])
        ur.soft_skills_match=methods.users.get_soft_skills_match(user_id, user["users"]["_id"])
        ooo.append(ur)
    return ooo
    # return [models.User(**user["users"], soft_skills_match=methods.users.get_soft_skills_match(user_id, user["users"]["_id"])) for user in to_return]
