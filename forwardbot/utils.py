from pyrogram import filters
from forwardbot import bot
from forwardbot.BotConfig import Config
bothandler = Config.COMMAND_HAND_LER

def forwardbot_cmd(add_cmd, is_args=False):
    """Create a Pyrogram command filter"""
    def cmd(func):
        # Pyrogram uses decorators, so we return the function with filter
        # The actual registration happens in the plugin files
        func._is_forwardbot_cmd = True
        func._cmd = add_cmd
        func._is_args = is_args
        return func
    return cmd

async def is_sudo(message):
    """Check if user is sudo user - works with Pyrogram Message object"""
    if hasattr(message, 'from_user') and message.from_user:
        return str(message.from_user.id) in Config.SUDO_USERS
    return False

def start_forwardbot(shortname):
    if shortname.startswith("__"):
        pass
    elif shortname.endswith("_"):
        import importlib
        import sys
        from pathlib import Path
        import forwardbot.utils
        path = Path(f"forwardbot/plugins/{shortname}.py")
        name = "forwardbot.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        print("Starting Your  Bot.")
        print("IMPORTED " + shortname)
    else:
        import importlib
        import sys
        from pathlib import Path
        import forwardbot.utils
        path = Path(f"forwardbot/plugins/{shortname}.py")
        name = "forwardbot.plugins.{}".format(shortname)
        spec = importlib.util.spec_from_file_location(name, path)
        mod = importlib.util.module_from_spec(spec)
        mod.forwardbot_cmd = forwardbot_cmd
        mod.forwardbot = bot
        mod.Config = Config
        spec.loader.exec_module(mod)
        sys.modules["forwardbot.plugins" + shortname] = mod
        print("IMPORTED " + shortname)
