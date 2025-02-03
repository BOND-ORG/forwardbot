from os import environ
class Config(object):
    API_ID = environ.get("API_ID", None)
    API_HASH = environ.get("API_HASH", None)
    BOT_TOKEN = environ.get("BOT_TOKEN", None)
    STRING_SESSION = environ.get("STRING", None)
    SUDO_USERS = environ.get("SUDO_USERS", None)
    COMMAND_HAND_LER = environ.get("COMMAND_HAND_LER", "^/")
    HELP_MSG = """
    The Commands in the bot are:
    
    **Command :** /forward
    **Usage : ** Forwards messages from a channel to other.
    **Command :** /help
    **Usage : ** Get the help of this bot.
    **Command :** /status
    **Usage :** Check current status of Bot.
    **Command :** /cancel
    **Usage :** To Restart Bot.
    """
