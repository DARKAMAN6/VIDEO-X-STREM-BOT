# Copyright (C) 2021 By Veez Music-Project
# Commit Start Date 20/10/2021
# Finished On 28/10/2021

import re
import asyncio

from config import ASSISTANT_NAME, BOT_USERNAME, ROYAL_IMG
from driver.filters import command, other_filters
from driver.queues import QUEUE, add_to_queue
from driver.veez import call_py, user
from pyrogram import Client
from pyrogram.errors import UserAlreadyParticipant, UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message
from pytgcalls import StreamType
from pytgcalls.types.input_stream import AudioVideoPiped
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from youtubesearchpython import VideosSearch


def ytsearch(query: str):
    try:
        search = VideosSearch(query, limit=1).result()
        data = search["result"][0]
        songname = data["title"]
        url = data["link"]
        duration = data["duration"]
        thumbnail = f"https://i.ytimg.com/vi/{data['id']}/hqdefault.jpg"
        return [songname, url, duration, thumbnail]
    except Exception as e:
        print(e)
        return 0


async def ytdl(link):
    proc = await asyncio.create_subprocess_exec(
        "yt-dlp",
        "-g",
        "-f",
        "best[height<=?720][width<=?1280]",
        f"{link}",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await proc.communicate()
    if stdout:
        return 1, stdout.decode().split("\n")[0]
    else:
        return 0, stderr.decode()


@Client.on_message(command(["vplay", f"vplay@{BOT_USERNAME}"]) & other_filters)
async def vplay(c: Client, m: Message):
    await m.delete()
    replied = m.reply_to_message
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ΰΌββ¨ππππΰΌββ€", callback_data="cbmenu"),
                InlineKeyboardButton(text="ΰΌβπΊπππππΰΌββ€", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous__ Admin !\n\nΒ» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"π‘ To use me, I need to be an **Administrator** with the following **permissions**:\n\nΒ» β __Delete messages__\nΒ» β __Add users__\nΒ» β __Manage video chat__\n\nData is **updated** automatically after you **promote me**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "missing required permission:" + "\n\nΒ» β __Manage video chat__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "missing required permission:" + "\n\nΒ» β __Delete messages__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("missing required permission:" + "\n\nΒ» β __Add users__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **is banned in group** {m.chat.title}\n\nΒ» **unban the userbot first if you want to use this bot.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"β **userbot failed to join**\n\n**reason**: `{e}`")
                return
        else:
            try:
                invitelink = await c.export_chat_invite_link(
                    m.chat.id
                )
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                await user.join_chat(invitelink)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"β **userbot failed to join**\n\n**reason**: `{e}`"
                )

    if replied:
        if replied.video or replied.document:
            loser = await replied.reply("**π₯π³πΎππ½π»πΎπ°π³πΈπ½πΆ ππΈπ³π΄πΎ**")
            dl = await replied.download()
            link = replied.link
            if len(m.command) < 2:
                Q = 720
            else:
                pq = m.text.split(None, 1)[1]
                if pq == "720" or "480" or "360":
                    Q = int(pq)
                else:
                    Q = 720
                    await loser.edit(
                        "Β» __only 720, 480, 360 allowed__ \nπ‘ **now streaming video in 720p**"
                    )
            try:
                if replied.video:
                    songname = replied.video.file_name[:70]
                elif replied.document:
                    songname = replied.document.file_name[:70]
            except BaseException:
                songname = "Video"

            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{ROYAL_IMG}",
                    caption=f"π‘ **πππ°π²πΊ π°π³π³π΄π³ ππΎ πππ΄ππ΄ Β»** `{pos}`\n\nπ· **π½π°πΌπ΄ β** [{songname}]({link}) | `ππΈπ³π΄πΎ`\nπ­ **π²π·π°π β** `{chat_id}`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                await loser.edit("**π₯π²πΎπ½π½π΄π²ππΈπ½πΆ ππΎ ππΎππ°π» ππ΄πππ΄ππ**")
                await call_py.join_group_call(
                    chat_id,
                    AudioVideoPiped(
                        dl,
                        HighQualityAudio(),
                        amaze,
                    ),
                    stream_type=StreamType().local_stream,
                )
                add_to_queue(chat_id, songname, dl, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{ROYAL_IMG}",
                    caption=f"π· **π½π°πΌπ΄ β** [{songname}]({link})\nπ­ **π²π·π°π β** `{chat_id}`\nπ‘ **πππ°πππ β** `πΏπ»π°ππΈπ½πΆ`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}\nπ±οΈ **ππππ΄π°πΌ πππΏπ΄ β** `ππΈπ³π΄πΎ`",
                    reply_markup=keyboard,
                )
        else:
            if len(m.command) < 2:
                await m.reply(
                    "Β» reply to an **video file** or **give something to search.**"
                )
            else:
                loser = await c.send_message(chat_id, "**ππΎππ°π» πΊπΈπ½πΆ πΎπ½ π΅πΈππ΄π₯**")
                query = m.text.split(None, 1)[1]
                search = ytsearch(query)
                Q = 720
                amaze = HighQualityVideo()
                if search == 0:
                    await loser.edit("β **no results found.**")
                else:
                    songname = search[0]
                    url = search[1]
                    duration = search[2]
                    thumbnail = search[3]
                    veez, ytlink = await ytdl(url)
                    if veez == 0:
                        await loser.edit(f"β yt-dl issues detected\n\nΒ» `{ytlink}`")
                    else:
                        if chat_id in QUEUE:
                            pos = add_to_queue(
                                chat_id, songname, ytlink, url, "Video", Q
                            )
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"π‘ **πππ°π²πΊ π°π³π³π΄π³ ππΎ πππ΄ππ΄ Β»** `{pos}`\n\nπ· **π½π°πΌπ΄ β** [{songname}]({url}) | `ππΈπ³π΄πΎ`\nβ± **π³πππ°ππΈπΎπ½ β** `{duration}`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}",
                                reply_markup=keyboard,
                            )
                        else:
                            try:
                                await loser.edit("**π₯π²πΎπ½π½π΄π²ππΈπ½πΆ ππΎ ππΎππ°π» ππ΄πππ΄ππ**")
                                await call_py.join_group_call(
                                    chat_id,
                                    AudioVideoPiped(
                                        ytlink,
                                        HighQualityAudio(),
                                        amaze,
                                    ),
                                    stream_type=StreamType().local_stream,
                                )
                                add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                                await loser.delete()
                                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                                await m.reply_photo(
                                    photo=thumbnail,
                                    caption=f"π· **π½π°πΌπ΄ β** [{songname}]({url})\nβ± **π³πππ°ππΈπΎπ½ β** `{duration}`\nπ‘ **πππ°πππ β** `Playing`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}\nπ±οΈ **ππππ΄π°πΌ πππΏπ΄ β** `ππΈπ³π΄πΎ`",
                                    reply_markup=keyboard,
                                )
                            except Exception as ep:
                                await loser.delete()
                                await m.reply_text(f"π« error: `{ep}`")

    else:
        if len(m.command) < 2:
            await m.reply(
                "Β» reply to an **video file** or **give something to search.**"
            )
        else:
            loser = await c.send_message(chat_id, "**ππΎππ°π» πΊπΈπ½πΆ πΎπ½ π΅πΈππ΄π₯**")
            query = m.text.split(None, 1)[1]
            search = ytsearch(query)
            Q = 720
            amaze = HighQualityVideo()
            if search == 0:
                await loser.edit("β **no results found.**")
            else:
                songname = search[0]
                url = search[1]
                duration = search[2]
                thumbnail = search[3]
                veez, ytlink = await ytdl(url)
                if veez == 0:
                    await loser.edit(f"β yt-dl issues detected\n\nΒ» `{ytlink}`")
                else:
                    if chat_id in QUEUE:
                        pos = add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                        await loser.delete()
                        requester = (
                            f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                        )
                        await m.reply_photo(
                            photo=thumbnail,
                            caption=f"π‘ **πππ°π²πΊ π°π³π³π΄π³ ππΎ πππ΄ππ΄ Β»** `{pos}`\n\nπ· **π½π°πΌπ΄ β** [{songname}]({url}) | `ππΈπ³π΄πΎ`\nβ± **π³πππ°ππΈπΎπ½ β** `{duration}`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}",
                            reply_markup=keyboard,
                        )
                    else:
                        try:
                            await loser.edit("**π₯π²πΎπ½π½π΄π²ππΈπ½πΆ ππΎ ππΎππ°π» ππ΄πππ΄ππ**")
                            await call_py.join_group_call(
                                chat_id,
                                AudioVideoPiped(
                                    ytlink,
                                    HighQualityAudio(),
                                    amaze,
                                ),
                                stream_type=StreamType().local_stream,
                            )
                            add_to_queue(chat_id, songname, ytlink, url, "Video", Q)
                            await loser.delete()
                            requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                            await m.reply_photo(
                                photo=thumbnail,
                                caption=f"π· **π½π°πΌπ΄ β** [{songname}]({url})\nβ± **π³πππ°ππΈπΎπ½ β** `{duration}`\nπ‘ **πππ°πππ β** `πΏπ»π°ππΈπ½πΆ`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}\nπ±οΈ **ππππ΄π°πΌ πππΏπ΄ β** `ππΈπ³π΄πΎ`",
                                reply_markup=keyboard,
                            )
                        except Exception as ep:
                            await loser.delete()
                            await m.reply_text(f"π« error: `{ep}`")


@Client.on_message(command(["vstream", f"vstream@{BOT_USERNAME}"]) & other_filters)
async def vstream(c: Client, m: Message):
    await m.delete()
    chat_id = m.chat.id
    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ΰΌββ¨ππππΰΌββ€", callback_data="cbmenu"),
                InlineKeyboardButton(text="ΰΌβπΊπππππΰΌββ€", callback_data="cls"),
            ]
        ]
    )
    if m.sender_chat:
        return await m.reply_text("you're an __Anonymous__ Admin !\n\nΒ» revert back to user account from admin rights.")
    try:
        aing = await c.get_me()
    except Exception as e:
        return await m.reply_text(f"error:\n\n{e}")
    a = await c.get_chat_member(chat_id, aing.id)
    if a.status != "administrator":
        await m.reply_text(
            f"π‘ To use me, I need to be an **Administrator** with the following **permissions**:\n\nΒ» β __Delete messages__\nΒ» β __Add users__\nΒ» β __Manage video chat__\n\nData is **updated** automatically after you **promote me**"
        )
        return
    if not a.can_manage_voice_chats:
        await m.reply_text(
            "missing required permission:" + "\n\nΒ» β __Manage video chat__"
        )
        return
    if not a.can_delete_messages:
        await m.reply_text(
            "missing required permission:" + "\n\nΒ» β __Delete messages__"
        )
        return
    if not a.can_invite_users:
        await m.reply_text("missing required permission:" + "\n\nΒ» β __Add users__")
        return
    try:
        ubot = (await user.get_me()).id
        b = await c.get_chat_member(chat_id, ubot)
        if b.status == "kicked":
            await m.reply_text(
                f"@{ASSISTANT_NAME} **is banned in group** {m.chat.title}\n\nΒ» **unban the userbot first if you want to use this bot.**"
            )
            return
    except UserNotParticipant:
        if m.chat.username:
            try:
                await user.join_chat(m.chat.username)
            except Exception as e:
                await m.reply_text(f"β **userbot failed to join**\n\n**reason**: `{e}`")
                return
        else:
            try:
                invitelink = await c.export_chat_invite_link(
                    m.chat.id
                )
                if invitelink.startswith("https://t.me/+"):
                    invitelink = invitelink.replace(
                        "https://t.me/+", "https://t.me/joinchat/"
                    )
                await user.join_chat(invitelink)
            except UserAlreadyParticipant:
                pass
            except Exception as e:
                return await m.reply_text(
                    f"β **userbot failed to join**\n\n**reason**: `{e}`"
                )

    if len(m.command) < 2:
        await m.reply("Β» give me a live-link/m3u8 url/youtube link to stream.")
    else:
        if len(m.command) == 2:
            link = m.text.split(None, 1)[1]
            Q = 720
            loser = await c.send_message(chat_id, "**π₯πΏππΎπ²π΄πππΈπ½πΆ ππππ΄π°πΌ**")
        elif len(m.command) == 3:
            op = m.text.split(None, 1)[1]
            link = op.split(None, 1)[0]
            quality = op.split(None, 1)[1]
            if quality == "720" or "480" or "360":
                Q = int(quality)
            else:
                Q = 720
                await m.reply(
                    "Β» __only 720, 480, 360 allowed__ \nπ‘ **now streaming video in 720p**"
                )
            loser = await c.send_message(chat_id, "**π₯πΏππΎπ²π΄πππΈπ½πΆ ππππ΄π°πΌ**")
        else:
            await m.reply("**/vstream {link} {720/480/360}**")

        regex = r"^(https?\:\/\/)?(www\.youtube\.com|youtu\.?be)\/.+"
        match = re.match(regex, link)
        if match:
            veez, livelink = await ytdl(link)
        else:
            livelink = link
            veez = 1

        if veez == 0:
            await loser.edit(f"β yt-dl issues detected\n\nΒ» `{livelink}`")
        else:
            if chat_id in QUEUE:
                pos = add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                await loser.delete()
                requester = f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                await m.reply_photo(
                    photo=f"{ROYAL_IMG}",
                    caption=f"π‘ **πππ°π²πΊ π°π³π³π΄π³ ππΎ πππ΄ππ΄ Β»** `{pos}`\n\nπ­ **π²π·π°π β** `{chat_id}`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}",
                    reply_markup=keyboard,
                )
            else:
                if Q == 720:
                    amaze = HighQualityVideo()
                elif Q == 480:
                    amaze = MediumQualityVideo()
                elif Q == 360:
                    amaze = LowQualityVideo()
                try:
                    await loser.edit("**π₯π²πΎπ½π½π΄π²ππΈπ½πΆ ππΎ ππΎππ°π» ππ΄πππ΄ππ**")
                    await call_py.join_group_call(
                        chat_id,
                        AudioVideoPiped(
                            livelink,
                            HighQualityAudio(),
                            amaze,
                        ),
                        stream_type=StreamType().live_stream,
                    )
                    add_to_queue(chat_id, "Live Stream", livelink, link, "Video", Q)
                    await loser.delete()
                    requester = (
                        f"[{m.from_user.first_name}](tg://user?id={m.from_user.id})"
                    )
                    await m.reply_photo(
                        photo=f"{ROYAL_IMG}",
                        caption=f"π‘ **[ππΈπ³π΄πΎ π»πΈππ΄]({link}) ππππ΄π°πΌ πππ°πππ΄π³.**\n\nπ­ **π²π·π°π β** `{chat_id}`\nπ‘ **πππ°πππ β** `πΏπ»π°ππΈπ½πΆ`\nπ§ **ππ΄πππ΄ππ π±π β** {requester}",
                        reply_markup=keyboard,
                    )
                except Exception as ep:
                    await loser.delete()
                    await m.reply_text(f"π« error: `{ep}`")
