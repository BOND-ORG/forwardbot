import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from forwardbot.BotConfig import Config
from forwardbot import bot
from forwardbot import client
from sys import argv
import glob
from pyrogram import idle
import asyncio

async def main():
    """Main function to start the bot and load plugins."""
    try:
        # Start both bot and client
        await bot.start()
        await client.start()
        
        # Set bot commands for the menu
        from pyrogram.types import BotCommand
        commands = [
            BotCommand("start", "Start the bot and see welcome message"),
            BotCommand("forward", "Forward messages (standard method)"),
            BotCommand("copy", "Copy from protected/restricted channels"),
            BotCommand("status", "Check current forwarding/copying status"),
            BotCommand("cancel", "Cancel operation and restart bot"),
            BotCommand("help", "Get detailed help information"),
        ]
        await bot.set_bot_commands(commands)
        print("✅ Bot commands menu configured")
        
        # Import all plugins
        path = "forwardbot/plugins/*.py"
        files = glob.glob(path)
        for name in files:
            with open(name) as f:
                path1 = Path(f.name)
                shortname = path1.stem
                # Import the module to register handlers
                if not shortname.startswith("__"):
                    try:
                        import importlib.util
                        spec = importlib.util.spec_from_file_location(f"forwardbot.plugins.{shortname}", name)
                        mod = importlib.util.module_from_spec(spec)
                        spec.loader.exec_module(mod)
                        print(f"Loaded plugin: {shortname}")
                    except Exception as e:
                        print(f"Failed to load {shortname}: {e}")

        print("Your BOT is Ready.")
        print("Try Sending /start")

        # Keep the bot running
        await idle()
    except KeyboardInterrupt:
        print("\n🛑 Received shutdown signal. Stopping bot...")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
    finally:
        # Cleanup
        try:
            await bot.stop()
            await client.stop()
            print("✅ Bot stopped gracefully")
        except:
            pass

if __name__ == "__main__":
    bot.run(main())
