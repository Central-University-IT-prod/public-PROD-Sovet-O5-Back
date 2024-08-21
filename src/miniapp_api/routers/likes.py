from os import getenv
from typing import Annotated, Literal

from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.exceptions import TelegramAPIError
 
from fastapi import APIRouter, Depends
from typing import Annotated, Literal

from miniapp_api.helpers import InitData, init_data_dependency
from database import models, methods


bot = Bot(token=getenv("BOT_TOKEN"))

def get_keyboard(user_id: int) -> InlineKeyboardBuilder:
    return InlineKeyboardBuilder().button(
        text="Перейти в мини-приложение",
        url=f"https://t.me/prod_the_O5_council_bot/LottieLink?startapp=user{user_id}"
    )

def get_text_like(name: str) -> str:
    return (
        f"{name} лайкнул(-а) твою анкету!\n"
        "Перейди в мини-приложение, чтобы узнать больше."
    )

def get_text_match(name: str, username: str) -> str:
    return (
        f"Поздравляем, ты и {name} лайкнули друг друга! 🎉 "
        f"Теперь вы можете связаться друг с другом: {username}.\n\n"
        "Я также отправил твой контакт собеседнику. Если у него нет никнейма, "
        "он все еще может связаться с тобой."
    )

def get_name(user: models.UserBase):
    assert user.profile is not None
    name = user.first_name
    if user.last_name is not None:
        name += " " + user.last_name
    return name

async def send_message_like(
    user_id: int,
    liked_user: models.User
) -> None:
    message = get_text_like(get_name(liked_user))
    try:
        await bot.send_message(
            user_id,
            message,
            reply_markup=get_keyboard(liked_user.id).as_markup()
        )
    except TelegramAPIError as e:
        print(e)

async def send_message_match(
    user_id: int,
    liked_user: models.User
) -> None:
    message = get_text_match(get_name(liked_user), liked_user.username)
    try:
        await bot.send_message(
            user_id,
            message,
            reply_markup=get_keyboard(liked_user.id).as_markup()
        )
    except TelegramAPIError as e:
        print(e)



router = APIRouter()

@router.post("/users/{target_id}/like")
async def handle_like(
    target_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    object_id = init_data.user_id
    methods.reactions.delete(models.Reaction(
        target_id=target_id,
        object_id=object_id,
        type=models.ReactionType.deferred.value
    ))

    # check reverse reaction
    if methods.reactions.get(models.Reaction(
        target_id=object_id,
        object_id=target_id,
        type=models.ReactionType.like.value
    )):
        # this is a match
        await send_message_match(target_id, methods.users.get_with_username(object_id))
        await send_message_match(object_id, methods.users.get_with_username(target_id))
        methods.reactions.delete(models.Reaction(
            target_id=object_id,
            object_id=target_id,
            type=models.ReactionType.like.value
        ))
        methods.reactions.create(models.Reaction(
            target_id=target_id,
            object_id=object_id,
            type=models.ReactionType.match.value
        ))
        methods.reactions.create(models.Reaction(
            target_id=object_id,
            object_id=target_id,
            type=models.ReactionType.match.value
        ))
    else:
        # this is a like
        await send_message_like(target_id, methods.users.get_with_username(object_id))
        methods.reactions.create(models.Reaction(
            target_id=target_id,
            object_id=object_id,
            type=models.ReactionType.like.value
        ))
    return {
        "ok": True
    }

@router.post("/users/{target_id}/dislike")
async def handle_dislike(
    target_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    object_id = init_data.user_id
    methods.reactions.delete(models.Reaction(
        target_id=target_id,
        object_id=object_id,
        type=models.ReactionType.deferred.value
    ))
    methods.reactions.create(models.Reaction(
        target_id=target_id,
        object_id=object_id,
        type=models.ReactionType.dislike.value
    ))
    methods.reactions.delete(models.Reaction(
        target_id=object_id,
        object_id=target_id,
        type=models.ReactionType.like.value
    ))
    return {
        "ok": True
    }

@router.post("/users/{target_id}/defer")
async def handle_defer(
    target_id: int,
    init_data: Annotated[InitData, Depends(init_data_dependency)]
):
    object_id = init_data.user_id
    methods.reactions.create(models.Reaction(
        target_id=target_id,
        object_id=object_id,
        type=models.ReactionType.deferred.value
    ))
    return {"ok": True}
