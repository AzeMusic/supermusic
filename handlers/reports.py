import os
from config import BOT_USERNAME 
from pyrogram import Client, filters
from pyrogram.types import Message, User



@Client.on_message(command(["report", f"report@{BOT_USERNAME}"]) & filters.group)
async def report(bot, message):
    if message.reply_to_message:
        chat_id = message.chat.id
        reporter = str(message.from_user.id)
        mention = message.from_user.mention
        admins = await bot.get_chat_members(chat_id=chat_id, filter="administrators")
        success = False
        report = f"Report verən : {mention} ({reporter})" + "\n"
        report += f"Mesaj : {message.reply_to_message.link}"
        for admin in admins:
            try:
                reported_post = await message.reply_to_message.forward(admin.user.id)
                await reported_post.reply_text(
                    text=report,
                    chat_id=admin.user.id,
                    disable_web_page_preview=True
                )
                success = True
            except:
                pass
        if success:
            await message.reply_text("**Adminlərə bildirildi!**")
