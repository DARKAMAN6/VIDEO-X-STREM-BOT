from cache.admins import admins
from driver.veez import call_py
from pyrogram import Client, filters
from driver.decorators import authorized_users_only
from driver.filters import command, other_filters
from driver.queues import QUEUE, clear_queue
from driver.utils import skip_current_song, skip_item
from config import BOT_USERNAME, GROUP_SUPPORT, ROYAL_IMG, UPDATES_CHANNEL
from pyrogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)


bttn = InlineKeyboardMarkup(
    [[InlineKeyboardButton("π±οΈπ±π°π²πΊ", callback_data="cbmenu")]]
)


bcl = InlineKeyboardMarkup(
    [[InlineKeyboardButton("ππ²π»πΎππ΄", callback_data="cls")]]
)


@Client.on_message(command(["reload", f"reload@{BOT_USERNAME}"]) & other_filters)
@authorized_users_only
async def update_admin(client, message):
    global admins
    new_admins = []
    new_ads = await client.get_chat_members(message.chat.id, filter="administrators")
    for u in new_ads:
        new_admins.append(u.user.id)
    admins[message.chat.id] = new_admins
    await message.reply_text(
        "β Bot **reloaded correctly !**\nβ **Admin list** has **updated !**"
    )


@Client.on_message(command(["skip", f"skip@{BOT_USERNAME}", "vskip"]) & other_filters)
@authorized_users_only
async def skip(client, m: Message):

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="β’ Mα΄Ι΄α΄", callback_data="cbmenu"
                ),
                InlineKeyboardButton(
                    text="β’ CΚα΄sα΄", callback_data="cls"
                ),
            ]
        ]
    )

    chat_id = m.chat.id
    if len(m.command) < 2:
        op = await skip_current_song(chat_id)
        if op == 0:
            await m.reply("β nothing is currently playing")
        elif op == 1:
            await m.reply("β __Queues__ **is empty.**\n\n**β’ userbot leaving voice chat**")
        elif op == 2:
            await m.reply("ποΈ **Clearing the Queues**\n\n**β’ userbot leaving voice chat**")
        else:
            await m.reply_photo(
                photo=f"{ROYAL_IMG}",
                caption=f"β­ **Skipped to the next track.**\n\nπ· **Name:** [{op[0]}]({op[1]})\nπ­ **Chat:** `{chat_id}`\nπ‘ **Status:** `Playing`\nπ§ **Request by:** {m.from_user.mention()}",
                reply_markup=keyboard,
            )
    else:
        skip = m.text.split(None, 1)[1]
        OP = "π **removed song from queue:**"
        if chat_id in QUEUE:
            items = [int(x) for x in skip.split(" ") if x.isdigit()]
            items.sort(reverse=True)
            for x in items:
                if x == 0:
                    pass
                else:
                    hm = await skip_item(chat_id, x)
                    if hm == 0:
                        pass
                    else:
                        OP = OP + "\n" + f"**#{x}** - {hm}"
            await m.reply(OP)


@Client.on_message(
    command(["stop", f"stop@{BOT_USERNAME}", "end", f"end@{BOT_USERNAME}", "vstop"])
    & other_filters
)
@authorized_users_only
async def stop(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await m.reply("β The userbot has disconnected from the video chat.")
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing is streaming**")


@Client.on_message(
    command(["pause", f"pause@{BOT_USERNAME}", "vpause"]) & other_filters
)
@authorized_users_only
async def pause(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await m.reply(
                "βΈ **Track paused.**\n\nβ’ **To resume the stream, use the**\nΒ» /resume command."
            )
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing in streaming**")


@Client.on_message(
    command(["resume", f"resume@{BOT_USERNAME}", "vresume"]) & other_filters
)
@authorized_users_only
async def resume(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await m.reply(
                "βΆοΈ **Track resumed.**\n\nβ’ **To pause the stream, use the**\nΒ» /pause command."
            )
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing in streaming**")


@Client.on_message(
    command(["mute", f"mute@{BOT_USERNAME}", "vmute"]) & other_filters
)
@authorized_users_only
async def mute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await m.reply(
                "π **Userbot muted.**\n\nβ’ **To unmute the userbot, use the**\nΒ» /unmute command."
            )
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing in streaming**")


@Client.on_message(
    command(["unmute", f"unmute@{BOT_USERNAME}", "vunmute"]) & other_filters
)
@authorized_users_only
async def unmute(client, m: Message):
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await m.reply(
                "π **Userbot unmuted.**\n\nβ’ **To mute the userbot, use the**\nΒ» /mute command."
            )
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing in streaming**")


@Client.on_callback_query(filters.regex("cbpause"))
async def cbpause(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nΒ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("π‘ only admin with manage voice chats permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.pause_stream(chat_id)
            await query.edit_message_text(
                "βΈ the streaming has paused", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"π« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("β nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbresume"))
async def cbresume(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nΒ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("π‘ only admin with manage voice chats permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.resume_stream(chat_id)
            await query.edit_message_text(
                "βΆοΈ the streaming has resumed", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"π« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("β nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbstop"))
async def cbstop(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nΒ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("π‘ only admin with manage voice chats permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.leave_group_call(chat_id)
            clear_queue(chat_id)
            await query.edit_message_text("β **this streaming has ended**", reply_markup=bcl)
        except Exception as e:
            await query.edit_message_text(f"π« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("β nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbmute"))
async def cbmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nΒ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("π‘ only admin with manage voice chats permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.mute_stream(chat_id)
            await query.edit_message_text(
                "π userbot succesfully muted", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"π« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("β nothing is currently streaming", show_alert=True)


@Client.on_callback_query(filters.regex("cbunmute"))
async def cbunmute(_, query: CallbackQuery):
    if query.message.sender_chat:
        return await query.answer("you're an Anonymous Admin !\n\nΒ» revert back to user account from admin rights.")
    a = await _.get_chat_member(query.message.chat.id, query.from_user.id)
    if not a.can_manage_voice_chats:
        return await query.answer("π‘ only admin with manage voice chats permission that can tap this button !", show_alert=True)
    chat_id = query.message.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.unmute_stream(chat_id)
            await query.edit_message_text(
                "π userbot succesfully unmuted", reply_markup=bttn
            )
        except Exception as e:
            await query.edit_message_text(f"π« **error:**\n\n`{e}`", reply_markup=bcl)
    else:
        await query.answer("β nothing is currently streaming", show_alert=True)


@Client.on_message(
    command(["volume", f"volume@{BOT_USERNAME}", "vol"]) & other_filters
)
@authorized_users_only
async def change_volume(client, m: Message):
    range = m.command[1]
    chat_id = m.chat.id
    if chat_id in QUEUE:
        try:
            await call_py.change_volume_call(chat_id, volume=int(range))
            await m.reply(
                f"β **volume set to** `{range}`%"
            )
        except Exception as e:
            await m.reply(f"π« **error:**\n\n`{e}`")
    else:
        await m.reply("β **nothing in streaming**")
