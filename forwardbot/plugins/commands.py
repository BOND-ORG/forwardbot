from forwardbot import Config, bot
from pyrogram import filters
from forwardbot.utils import is_sudo

MessageCount = 0

BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
help_msg = Config.HELP_MSG
sudo_users = Config.SUDO_USERS

@bot.on_message(filters.command("start"))
async def start_command(client, message):
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    start_message = """**👋 Welcome to Forward Bot!**

Use these commands to control the bot:

/forward - Forward messages (standard method)
/copy - Copy from protected/restricted channels
/cancel - Stop ongoing process
/status - Check current status
/help - Get detailed help

**📌 Two Methods Available:**
• **Forward**: Fast, standard forwarding
• **Copy**: Download & re-upload for protected channels

**⚠️ USE AT OWN RISK - ACCOUNT MAY GET BANNED**
"""
    await message.reply(start_message)               


@bot.on_message(filters.command("help"))
async def help_command(client, message):
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    await message.reply(help_msg)

