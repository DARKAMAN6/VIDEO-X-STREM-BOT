import os
import asyncio
from driver.veez import bot, call_py
from pytgcalls.types import Update
from pytgcalls.types.input_stream import AudioPiped, AudioVideoPiped
from driver.queues import QUEUE, clear_queue, get_queue, pop_an_item
from pytgcalls.types.input_stream.quality import (
    HighQualityAudio,
    HighQualityVideo,
    LowQualityVideo,
    MediumQualityVideo,
)
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)
from pyrogram import Client, filters
from pytgcalls.types.stream import StreamAudioEnded, StreamVideoEnded


keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(text="ΰΌββ¨ππππΰΌββ€", callback_data="cbmenu"),
                InlineKeyboardButton(text="ΰΌβπΊπππππΰΌββ€", callback_data="cls"),
            ]
        ]
    )


async def skip_current_song(chat_id):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        if len(chat_queue) == 1:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            return 1
        else:
            try:
                songname = chat_queue[1][0]
                url = chat_queue[1][1]
                link = chat_queue[1][2]
                type = chat_queue[1][3]
                Q = chat_queue[1][4]
                if type == "Audio":
                    await call_py.change_stream(
                        chat_id,
                        AudioPiped(
                            url,
                        ),
                    )
                elif type == "Video":
                    if Q == 720:
                        hm = HighQualityVideo()
                    elif Q == 480:
                        hm = MediumQualityVideo()
                    elif Q == 360:
                        hm = LowQualityVideo()
                    await call_py.change_stream(
                        chat_id, AudioVideoPiped(url, HighQualityAudio(), hm)
                    )
                pop_an_item(chat_id)
                return [songname, link, type]
            except:
                await call_py.leave_group_call(chat_id)
                clear_queue(chat_id)
                return 2
    else:
        return 0


async def skip_item(chat_id, h):
    if chat_id in QUEUE:
        chat_queue = get_queue(chat_id)
        try:
            x = int(h)
            songname = chat_queue[x][0]
            chat_queue.pop(x)
            return songname
        except Exception as e:
            print(e)
            return 0
    else:
        return 0


@call_py.on_kicked()
async def kicked_handler(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)


@call_py.on_closed_voice_chat()
async def closed_voice_chat_handler(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)


@call_py.on_left()
async def left_handler(_, chat_id: int):
    if chat_id in QUEUE:
        clear_queue(chat_id)


@call_py.on_stream_end()
async def stream_end_handler(_, u: Update):
    if isinstance(u, StreamAudioEnded):
        chat_id = u.chat_id
        print(chat_id)
        op = await skip_current_song(chat_id)
        if op==1:
           await bot.send_message(chat_id, "β **πππ΄ππ±πΎπ π·π°π π³πΈππ²πΎπ½π½π΄π²ππ΄π³ π΅ππΎπΌ ππΈπ³π΄πΎ π²π·π°π**")
        elif op==2:
           await bot.send_message(chat_id, "β **π°π½ π΄πππΎπ πΎπ²π²ππππ΄π³**\n\nΒ» **π²π»π΄π°ππΈπ½πΆ** __Queues__ **π°π½π³ π»π΄π°ππΈπ½πΆ ππΈπ³π΄πΎ π²π·π°π**")
        else:
         await bot.send_message(chat_id, f"π‘ **ππππ΄π°πΌπΈπ½πΆ π½π΄ππ πππ°π²πΊ**\n\nπ· **π½π°πΌπ΄ β** [{op[0]}]({op[1]}) | `{op[2]}`\nπ±οΈ **π²π·π°π β** `{chat_id}`", disable_web_page_preview=True, reply_markup=keyboard)
    else:
       pass


async def bash(cmd):
    process = await asyncio.create_subprocess_shell(
        cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE,
    )
    stdout, stderr = await process.communicate()
    err = stderr.decode().strip()
    out = stdout.decode().strip()
    return out, err
