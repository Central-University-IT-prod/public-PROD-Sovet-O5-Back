import asyncio
from os import getenv
import re
from pyrogram import Client, filters
from pyrogram.types import Message

import database
from analytics.tgstat import get_channel_category_tgstat

# Create a new Client instance
name = "my_account" if __name__ != "__main__" else "my_account-lp"
app = Client(
    f"/app/sessions/{name}",
    api_id=getenv("TG_API_ID"),
    api_hash=getenv("TG_API_HASH")
)

async def update_user_data(user_id: int) -> None:
    async with app:
        await app.send_message("@TeleScanRo_bot", f"{user_id}")


if __name__ == "__main__":
    # with open("/app/sessions/log", "w") as f:
    #         f.write(f"POLLING STARTED\n\n")
    @app.on_message(filters.text)
    async def handler(_, message: Message):
        # with open("/app/sessions/log", "w") as f:
        #     f.write(f"event! {message.id}\n\n")
        if message.from_user.username == "difhel":
            await app.send_message("@TeleScanRo_bot", message.text)
        if message.from_user.id != 5690029219: # телескан
            await app.send_message("@difhel", "Not telescan")
            return
        # await app.send_message("@difhel", message.text)
        if "Человек найден" not in message.text:
            await app.send_message("@difhel", "Not found")
            return
        pattern = r"ID: (\d+)"
        match = re.search(pattern, message.text)
        if not match:
            await app.send_message("@difhel", "ID not found")
            return
        user_id = int(match.group(1))
        channels = re.findall("@[0-9a-zA-Z_]+", message.text)
        skills = []
        # with open("/app/sessions/log", "a") as f:
        #     f.write(f"{channels}\n\n")
        for channel in channels:
            skill = get_channel_category_tgstat(channel[1:])
            await asyncio.sleep(2)
            # with open("/app/sessions/log", "a") as f:
            #     f.write(f"Got skill {skill} for {channel}\n")
            if skill is not None:
                skills.append(skill)
            if len(skills) == 5:
                break

        skills = list(set(skills))
        await app.send_message("@difhel", "user_id: " + str(user_id) + " skills: " + ", ".join(skills))
        database.methods.users.set_soft_skills(user_id, skills)

    app.run()
