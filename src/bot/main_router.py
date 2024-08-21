import os
from aiogram import Router, F
from aiogram.filters import CommandStart, CommandObject
import aiohttp
from bot import helpers
import database
import random
from os import getenv
from aiogram.types import Message, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardMarkup
from aiogram.types import InlineKeyboardButton
import bot.main_locales as locales
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext
import tempfile
import json



router = Router()


class CallbackPrefixes:
    insert_allowed_usernames = "insert_allowed_usernames"
    insert_special_data = "insert_special_data"


class States(StatesGroup):
    main = State()
    insert_special_data = State()


@router.message(CommandStart(deep_link=True))
@router.message(CommandStart())
async def start(message: Message, command: CommandObject, state: FSMContext):
    args = command.args
    
    await state.clear()
    await state.set_state(States.main)
    await helpers.avatars.download_user_avatar(message.bot, message.from_user)
    
    admin_mk = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=locales.go_to_admin_web_page(),
                    url="https://t.me/prod_the_O5_council_bot/LottieLink?startapp=admin" #  TODO: add web_app link
                )
            ],
            [
                InlineKeyboardButton(
                    text=locales.insert_special_data(),
                    callback_data=CallbackPrefixes.insert_special_data,
                )   
            ]
        ]
    )
    
    admin_miniapp_message = message.answer(
        text=locales.admin_miniapp_message(),
        reply_markup=admin_mk
    )
    
    
    member_mk = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=locales.go_to_member_web_page(),
                    url="https://t.me/prod_the_O5_council_bot/LottieLink?startapp=profile" #  TODO: add web_app link
                )
            ]       
        ]
    )
    
    member_miniapp_message = message.answer(
        text=locales.member_miniapp_message(),
        reply_markup=member_mk    
    )

    
    if args is None:
        #  check user access
        is_admin = database.methods.admins_ids.check_admin_access_by_id(
            message.from_user.id
        )
        if is_admin:
            # here message to go to admin miniapp
            return await admin_miniapp_message
        
        special_data = database.methods.special_data.get_special_data_by_username(
            message.from_user.username
        )
        
        if os.getenv("WHITELIST") == "DISABLED":
            special_data = database.models.SpecialData(
                id=message.from_user.username,
                score=round(random.random() * 100, 2),
                position=random.choice(["frontend", "backend", "mobile"])
            )  # генерируем случайную специальную информацию для незареганых пользователей
            
        
        if special_data is not None:
            user = database.methods.users.is_user_exists(
                message.from_user.id
            )

            if not user: #  if user first in the app
                user_to_create = database.models.User(
                    id=message.from_user.id,
                    rating=special_data.score,
                    score=special_data.score,
                    username=message.from_user.username,
                    team_id=message.from_user.id,
                    profile=None,
                    first_name=message.from_user.first_name,
                    last_name=message.from_user.last_name
                )

                database.methods.users.create(
                    user_to_create
                )

                team_to_create = database.models.Team(
                    id=message.from_user.id,
                    lead=message.from_user.id,   
                    name="",
                    description=""
                )

                database.methods.teams.create_individual(
                    team_to_create
                )

                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        f"http://localhost:4242/soft-skills?user_id={user.id}",
                        headers={
                            "Authorization": f"""Service {getenv(
                                'SERVICE_API_TOKEN'
                            )}"""
                        }
                    ) as _response:
                        pass


            # here message to go to member miniapp
            return await member_miniapp_message
        
        return await message.answer(
            text=locales.auth_error()
        )
        
    SK = getenv("ADMIN_SECRET_START_PARAM")
            
    if args == SK:
        is_admin = database.methods.admins_ids.check_admin_access_by_id(
            message.from_user.id
        )
        if not is_admin:
            database.methods.admins_ids.create_admin(
                message.from_user.id
            )
        # here message to go to admin miniapp
        return await admin_miniapp_message
    await message.answer(
        text=locales.wrong_secret()
    )
    

@router.callback_query(States.main, F.data == CallbackPrefixes.insert_special_data)
async def insert_special_data(
    callback: CallbackQuery,
    state: FSMContext
):
    await state.set_state(States.insert_special_data)
    
    await callback.message.answer(
        text=locales.insert_special_data_main(),
    )
    
    await callback.answer()


@router.message(States.insert_special_data, F.document)
async def handle_special_data_file(
    message: Message,
    state: FSMContext
):
    
    json_data = ""
    
    file = (await message.bot.get_file(message.document.file_id)).file_path

    if len(file.split('.')) < 2 or file.split('.')[-1] != "json":
        return await message.answer(
            text=locales.json_load_error()
        )
    
    with tempfile.NamedTemporaryFile() as tmp:
        await message.bot.download_file(file, tmp.name)
        
        with open(tmp.name, "r", encoding="utf-8") as f:
            json_data = f.read().strip()
    
    try:
        json_parsed_data = json.loads(json_data)
        
        database.methods.special_data.insert_special_data(
            json_parsed_data
        )

    except Exception as e:
        return await message.answer(
            text=locales.json_load_error()
        )
                
    await message.answer(
        text=locales.successful_insert_special_data()
    )
    await state.clear()


