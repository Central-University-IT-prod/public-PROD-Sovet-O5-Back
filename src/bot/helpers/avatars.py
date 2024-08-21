"""Helper module for downloading avatars from Telegram"""
import os
import aiogram
import aiohttp


async def download_user_avatar(bot: aiogram.Bot, user: aiogram.types.User) -> None:
    """
    Async function to download the avatar of the given user and save it to the specified folder.

    Args:
        bot (aiogram.Bot): bot instance
        user (aiogram.types.User): user whose avatar will be downloaded
    """
    filepath = os.path.join("/app/avatars", f"{user.id}.jpg")
    if os.path.exists(filepath):
        return
    photos = await user.get_profile_photos()
    if not photos.photos:
        return
    if (telegram_filepath := (await bot.get_file(photos.photos[0][-1].file_id)).file_path) is None:
        return
    await bot.download_file(telegram_filepath, filepath)
    if os.getenv("SERVICE_API_URL") is not None:
        # API is being runned on another host
        # we use service API method to upload the avatar
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{os.getenv('SERVICE_API_URL')}/avatars/uploadAvatar?id={user.id}",
                data={
                    "avatar": open(filepath, "rb")
                },
                headers={"Authorization": f"Service {os.getenv('SERVICE_API_TOKEN')}"}
            ) as _response:
                pass
