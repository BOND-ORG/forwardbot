import sys
import logging
from logging import DEBUG, WARNING, basicConfig, getLogger, INFO
import os
import asyncio

from pyrogram import Client
from distutils.util import strtobool as sb
from pyrogram import filters
ENV = True

if ENV:
    from forwardbot.BotConfig import Config
else:
    from local_config import Development as Config

bot = Client(
    "bot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN
)

client = Client(
    "user_session",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.STRING_SESSION
)

# Store pending conversations for listen pattern
pending_conversations = {}

# Simple listen implementation for Pyrogram
async def listen(client_instance, chat_id, timeout=300):
    """Wait for next message from user in chat"""
    future = asyncio.Future()
    pending_conversations[chat_id] = future
    
    try:
        result = await asyncio.wait_for(future, timeout=timeout)
        return result
    finally:
        if chat_id in pending_conversations:
            del pending_conversations[chat_id]

# Add listen method to both clients
client.listen = lambda chat_id: listen(client, chat_id)
bot.listen = lambda chat_id: listen(bot, chat_id)

if bool(ENV):
    CONSOLE_LOGGER_VERBOSE = sb(os.environ.get("CONSOLE_LOGGER_VERBOSE", "False"))

    if CONSOLE_LOGGER_VERBOSE:
        basicConfig(
            format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s",
            level=DEBUG,
        )
    else:
        basicConfig(
            format="[%(levelname) 5s/%(asctime)s] %(name)s: %(message)s", level=INFO
        )
    
    # Custom filter to suppress peer resolution errors
    class SuppressPeerErrors(logging.Filter):
        def filter(self, record):
            # Suppress "Peer id invalid" errors
            if "Peer id invalid" in str(record.msg):
                return False
            # Suppress "Task exception was never retrieved" for peer errors
            if "Task exception was never retrieved" in str(record.msg) and "Peer id invalid" in str(record.exc_info):
                return False
            return True
    
    # Apply filter to Pyrogram loggers
    peer_filter = SuppressPeerErrors()
    logging.getLogger("pyrogram.dispatcher").addFilter(peer_filter)
    logging.getLogger("pyrogram.dispatcher").setLevel(WARNING)
    logging.getLogger("pyrogram.connection.connection").setLevel(WARNING)
    logging.getLogger("asyncio").addFilter(peer_filter)
    
    logger = getLogger(__name__)

if Config.API_ID is None:
    logger.info("API_ID is None. Bot Is Quiting")
    sys.exit(1)
if Config.API_HASH is None:
    logger.info("API_HASH is None. Bot Is Quiting")
    sys.exit(1)
if Config.BOT_TOKEN is None:
    logger.info("BOT_TOKEN is None. Bot Is Quiting")
    sys.exit(1)
if Config.STRING_SESSION is None:
    logger.info("STRING_SESSION is None. Bot Is Quiting")
    sys.exit(1)
if Config.SUDO_USERS is None:
    logger.info("SUDO_USERS is None. Bot Is Quiting")
    sys.exit(1)

async def is_sudo(message):
    """Check if user is sudo user - works with Pyrogram Message object"""
    if hasattr(message, 'from_user') and message.from_user:
        return str(message.from_user.id) in Config.SUDO_USERS
    return False

@bot.on_message(filters.command("cancel"))
async def cancel_handler(client, message):
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    try:
        await message.reply('🔄 Cancelling current operation and restarting bot...')
        # Give time for the message to be sent
        await asyncio.sleep(1)
        # Exit the process
        os._exit(0)
    except Exception as e:
        await message.reply(f'❌ Error during restart: {str(e)}')
