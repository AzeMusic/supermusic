import os
import time
import ffmpeg
import asyncio
from os import path
from asyncio import sleep
from config import Config
from bot.safone.nopm import User
from youtube_dl import YoutubeDL
from pyrogram import Client, filters
from pyrogram.types import Message
from pyrogram.errors import FloodWait
from pytgcalls import GroupCallFactory
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

ADMINS = Config.SUDO_USER
CHAT_ID = Config.CHAT_ID
USERNAME = Config.BOT_USERNAME

STREAM = {6}
VIDEO_CALL = {}

ydl_opts = {
        "format": "best",
        "addmetadata": True,
        "geo_bypass": True,
        "nocheckcertificate": True,
        "videoformat": "mp4",
        "outtmpl": "downloads/%(id)s.%(ext)s",
}
ydl = YoutubeDL(ydl_opts)
group_call_factory = GroupCallFactory(User, GroupCallFactory.MTPROTO_CLIENT_TYPE.PYROGRAM)

@Client.on_message(filters.command(["stream", f"stream@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def stream(client, m: Message):
    if 1 in STREAM:
        await m.reply_text("🤖 **Please Stop The Existing Stream!**")
        return

    media = m.reply_to_message
    if not media and not ' ' in m.text:
        await m.reply("❗ __Send Me An YouTube Link or Reply To An Video To Start Streaming On VC!__")

    elif ' ' in m.text:
        msg = await m.reply_text("🔄 `Downloading ...`")
        text = m.text.split(' ', 1)
        url = text[1]
        if os.path.exists(f'stream-{CHAT_ID}.raw'):
            os.remove(f'stream-{CHAT_ID}.raw')
        try:
            info = ydl.extract_info(url, False)
            ydl.download([url])
            video = path.join("downloads", f"{info['id']}.{info['ext']}")
            await msg.edit("🔄 `Transcoding ...`")
            os.system(f'ffmpeg -i "{video}" -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le -filter:a "atempo=0.81" stream-{CHAT_ID}.raw -y')
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n\nError: `{e}`")
        await sleep(5)
        group_call = group_call_factory.get_file_group_call(f'stream-{CHAT_ID}.raw')
        try:
            await group_call.start(CHAT_ID)
            await group_call.set_video_capture(video)
            VIDEO_CALL[CHAT_ID] = group_call
            await msg.edit("▶️ **Started Streaming!**")
            try:
                STREAM.remove(0)
            except:
                pass
            try:
                STREAM.add(1)
            except:
                pass
        except FloodWait as e:
            await sleep(e.x)
            if not group_call.is_connected:
                await group_call.start(CHAT_ID)
                await group_call.set_video_capture(video)
                VIDEO_CALL[CHAT_ID] = group_call
                await msg.edit("▶️ **Started Streaming!**")
                try:
                    STREAM.remove(0)
                except:
                    pass
                try:
                    STREAM.add(1)
                except:
                    pass
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n\nError: `{e}`")

    elif media.video or media.document:
        msg = await m.reply_text("🔄 `Downloading ...`")
        if os.path.exists(f'stream-{CHAT_ID}.raw'):
            os.remove(f'stream-{CHAT_ID}.raw')
        try:
            video = await client.download_media(media)
            await msg.edit("🔄 `Transcoding ...`")
            os.system(f'ffmpeg -i "{video}" -vn -f s16le -ac 2 -ar 48000 -acodec pcm_s16le -filter:a "atempo=0.81" stream-{CHAT_ID}.raw -y')
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n\nError: `{e}`")
        await sleep(5)
        group_call = group_call_factory.get_file_group_call(f'stream-{CHAT_ID}.raw')
        try:
            await group_call.start(CHAT_ID)
            await group_call.set_video_capture(video)
            VIDEO_CALL[CHAT_ID] = group_call
            await msg.edit("▶️ **Started Streaming!**")
            try:
                STREAM.remove(0)
            except:
                pass
            try:
                STREAM.add(1)
            except:
                pass
        except FloodWait as e:
            await sleep(e.x)
            if not group_call.is_connected:
                await group_call.start(CHAT_ID)
                await group_call.set_video_capture(video)
                VIDEO_CALL[CHAT_ID] = group_call
                await msg.edit("▶️ **Started Streaming!**")
                try:
                    STREAM.remove(0)
                except:
                    pass
                try:
                    STREAM.add(1)
                except:
                    pass
        except Exception as e:
            await msg.edit(f"❌ **An Error Occoured!** \n\nError: `{e}`")
    else:
        await m.reply_text("❗ __Send Me An YouTube Link or Reply To An Video To Start Streaming On VC!__")
        return


@Client.on_message(filters.command(["mute", f"mute@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def mute(_, m: Message):
    if 0 in STREAM:
        await m.reply_text("🤖 **Please Start The Stream First!**")
        return
    try:
        await VIDEO_CALL[CHAT_ID].set_is_mute(True)
        await m.reply_text("🔇 **Muted Streamer!**")
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n\nError: `{e}`")


@Client.on_message(filters.command(["unmute", f"unmute@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def unmute(_, m: Message):
    if 0 in STREAM:
        await m.reply_text("🤖 **Please Start The Stream First!**")
        return
    try:
        await VIDEO_CALL[CHAT_ID].set_is_mute(False)
        await m.reply_text("🔉 **Unmuted Streamer!**")
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n\nError: `{e}`")


@Client.on_message(filters.command(["endstream", f"endstream@{USERNAME}"]) & filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def endstream(client, m: Message):
    if 0 in STREAM:
        await m.reply_text("🤖 **Please Start The Stream First!**")
        return
    try:
        await VIDEO_CALL[CHAT_ID].stop()
        await m.reply_text("⏹️ **Stopped Streaming!**")
        try:
            STREAM.remove(1)
        except:
            pass
        try:
            STREAM.add(0)
        except:
            pass
    except Exception as e:
        await m.reply_text(f"❌ **An Error Occoured!** \n\nError: `{e}`")


admincmds=["stream", "mute", "unmute", "endstream", f"stream@{USERNAME}", f"mute@{USERNAME}", f"unmute@{USERNAME}", f"endstream@{USERNAME}"]

@Client.on_message(filters.command(admincmds) & ~filters.user(ADMINS) & (filters.chat(CHAT_ID) | filters.private))
async def notforu(_, m: Message):
    k = await m.reply_sticker("CAACAgUAAxkBAAEBpyZhF4R-ZbS5HUrOxI_MSQ10hQt65QACcAMAApOsoVSPUT5eqj5H0h4E")
    await sleep(5)
    await k.delete()
    try:
        await m.delete()
    except:
        pass

allcmd = ["st", "lp", f"st@{USERNAME}", f"lp@{USERNAME}"] + admincmds

@Client.on_message(filters.command(allcmd) & filters.group & ~filters.chat(CHAT_ID))
async def not_chat(_, m: Message):
    buttons = [
            [
                InlineKeyboardButton("CHANNEL", url="https://t.me/AsmSafone"),
                InlineKeyboardButton("SUPPORT", url="https://t.me/SafoTheBot"),
            ],
            [
                InlineKeyboardButton("🤖 MAKE YOUR OWN BOT 🤖", url="https://heroku.com/deploy?template=https://github.com/AsmSafone/VideoPlayerBot"),
            ]
         ]
    await m.reply_text(text="**Sorry, You Can't Use This Bot In This Group 🤷‍♂️! But You Can Make Your Own Bot Like This From The [Source Code](https://github.com/AsmSafone/VideoPlayerBot) Below 😉!**", reply_markup=InlineKeyboardMarkup(buttons), disable_web_page_preview=True)
