from forwardbot import Config
from telethon.tl.functions.users import GetFullUserRequest
from forwardbot.utils import forwardbot_cmd
from forwardbot.utils import is_sudo
from forwardbot import bot

MessageCount = 0

BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
help_msg = Config.HELP_MSG
sudo_users = Config.SUDO_USERS

@forwardbot_cmd("start", is_args=False)
async def start(event):
    if not await is_sudo(event):
        await event.respond("You are not authorized to use this Bot. Create your own.")
        return
    start_message = """**👋 Welcome to Forward Bot!**

Use these commands to control the bot:

/forward - Start forwarding messages
/cancel - Stop ongoing forwarding
/status - Check current status
/help - Get detailed help

To start forwarding, use /forward and follow the instructions.

**⚠️ USE AT OWN RISK - ACCOUNT MAY GET BANNED**
"""
    await event.respond(start_message)               


@forwardbot_cmd("help", is_args=False)
async def handler(event):
    if not await is_sudo(event):
        await event.respond("You are not authorized to use this Bot. Create your own.")
        return
    await event.respond(help_msg)

@forwardbot_cmd("test", is_args=False)
async def handler(event):
    await event.respond(bot.owner)



@forwardbot_cmd("admin", is_args=False)
async def handler(event):
    if str(event.sender_id) in sudo_users:
        await event.respond("You are an admin")
    else:
        await event.respond("You are not an admin")


