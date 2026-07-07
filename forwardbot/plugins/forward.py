from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from forwardbot import bot, client as user_client, Config
from forwardbot.utils import is_sudo
from forwardbot.tool import *
import asyncio
import datetime
from datetime import timedelta
import random
import sys
import os
import pytz

MessageCount = 0
BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'

start = None
last_message_id = None
message_limit = 0
ist = pytz.timezone('Asia/Kolkata')

async def format_status_message(message_count, start_time, current_type):
    global last_message_id
    
    # Calculate uptime
    current_time = datetime.datetime.now()
    if start_time:
        diff = current_time - datetime.datetime.strptime(start_time, datetimeFormat)
        days, seconds = diff.days, diff.seconds
        hours = int(seconds / 3600)
        minutes = int((seconds % 3600)/60)
        seconds = int(seconds % 60)
    else:
        days = hours = minutes = seconds = 0
    
    status_message = f"""📊 **Forward Bot Status**
    
⏱ **Uptime**: {days}d {hours}h {minutes}m {seconds}s
📤 **Total Forwarded**: {message_count} messages
📝 **Last Message ID**: `{last_message_id or 'None'}`
🔍 **Channel ID**: `{fromchannel or 'None'}`

⚡ **Status**: {('Forwarding' if current_type in ['Document', 'Photo', 'Video', 'All'] else current_type)}
"""

    return status_message

# ❌ Use /cancel to stop forwarding
#  ⚡ **Status**: {'Active' if '1' in status else 'Sleeping' if '2' in status else 'Completed' if '3' in status else 'Idle' }

@bot.on_message(filters.command("forward"))
async def forward_command(client, message):
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    if "1" in status:
        await message.reply("A task is already running.")
        return
    if "2" in status:
        await message.reply("Sleeping the engine for avoiding ban.")
        return
    if "3" in status:
        await message.reply("The task is completed.")
        return
    
    # Step 1: Ask for channel
    await message.reply("Please send the channel id from where you want to forward messages.")
    response = await client.listen(message.chat.id)
    global fromchannel
    fromchannel = response.text.strip()
    
    # Step 2: Ask for message limit
    await message.reply("Select how many messages you want to forward, 0 for unlimited")
    response = await client.listen(message.chat.id)
    global message_limit
    message_limit = response.text.strip()
    
    # Step 3: Ask for offset
    await message.reply("Okay now send me the message id from where you want to start forwarding (0 if you want to forward from beginning)")
    response = await client.listen(message.chat.id)
    global offsetid
    offsetid = response.text.strip()
    
    # Step 4: Show buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('All Messages', callback_data='all'),
            InlineKeyboardButton('Only Photos', callback_data='photo')
        ],
        [
            InlineKeyboardButton('Only Documents', callback_data='docs'),
            InlineKeyboardButton('Only Video', callback_data='video')
        ]
    ])
    await message.reply('Select What you need to forward', reply_markup=keyboard)

@bot.on_message(filters.command("status"))
async def status_command(client, message):
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    
    if start:
        status_message = await format_status_message(MessageCount, start, "Current")
        await message.reply(status_message)
    else:
        current_status = "Running" if "1" in status else "Sleeping" if "2" in status else "Completed" if "3" in status else "Idle"
        await message.reply(f"Bot Status: {current_status}")

@bot.on_callback_query(filters.regex(r'^(all|docs|photo|video)$'))
async def forward_handler(client, callback_query):
    # Determine type based on callback data
    if callback_query.data == 'all':
        type = "All"
        await callback_query.message.delete()
    elif callback_query.data == 'docs':
        type = "Document"
        await callback_query.message.delete()
    elif callback_query.data == 'photo':
        type = "Photo"
        await callback_query.message.delete()
    elif callback_query.data == 'video':
        type = "Video"
        await callback_query.message.delete()
    else:
        return
    
    # Check authorization
    user_id = callback_query.from_user.id if callback_query.from_user else None
    if user_id is None or str(user_id) not in Config.SUDO_USERS:
        await callback_query.message.reply("You are not authorized to use this Bot. Create your own.")
        return
    if "1" in status:
        await callback_query.message.reply("A task is already running.")
        return
    if "2" in status:
        await callback_query.message.reply("Sleeping the engine for avoiding ban.")
        return
    if "3" in status:
        await callback_query.message.reply("The task is completed.")
        return
    
    try:
        m = await callback_query.message.reply("Initializing forwarding...")
        fromchat = int(fromchannel)
        tochat = int("-1002332846289")
        # Ensure source channel is accessible
        try:
            await m.edit("🔍 Accessing source channel...")
            chat_info = await user_client.get_chat(fromchat)
            await m.edit(f"✅ Source: {chat_info.title}")
        except Exception as source_error:
            error_str = str(source_error)
            if "CHANNEL_INVALID" in error_str or "Peer id invalid" in error_str:
                await m.edit("⚠️ Source not in cache, scanning dialogs...\nThis may take a moment.")
                found = False
                async for dialog in user_client.get_dialogs(limit=None):
                    if dialog.chat.id == fromchat:
                        found = True
                        await m.edit(f"✅ Found source: {dialog.chat.title}")
                        break
                if not found:
                    await m.edit(f"❌ Source channel {fromchat} not found.\n\nMake sure you've joined it with your user account.")
                    return
            else:
                raise source_error
        # Ensure destination channel is accessible
        try:
            await m.edit("🔍 Accessing destination channel...")
            dest_info = await user_client.get_chat(tochat)
            await m.edit(f"✅ Destination: {dest_info.title}")
        except Exception as dest_error:
            error_str = str(dest_error)
            if "CHANNEL_INVALID" in error_str or "Peer id invalid" in error_str:
                await m.edit("⚠️ Destination not in cache, scanning dialogs...")
                found = False
                async for dialog in user_client.get_dialogs(limit=None):
                    if dialog.chat.id == tochat:
                        found = True
                        await m.edit(f"✅ Found destination: {dialog.chat.title}")
                        break
                if not found:
                    await m.edit(f"❌ Destination channel {tochat} not found.\n\nMake sure you've joined it with your user account.")
                    return
            else:
                raise dest_error
        count = random.randint(468, 517)
        mcount = random.randint(86, 98)
        global MessageCount, start, last_message_id
        offset = 0 if offsetid == "0" else int(offsetid) - 1
        print("Starting to forward")
        start = str(datetime.datetime.now())
        last_status_update = datetime.datetime.now()

        if offsetid == "0":
            message_id = 1
            while True:
                try:
                    message = await user_client.get_messages(fromchat, message_id)
                    if not message:
                        break
                except:
                    break
                # Process message here
                if message_limit != "0" and MessageCount >= int(message_limit):
                    status.add("3")
                    status.remove("1")
                    await m.edit(await format_status_message(MessageCount, start, "Completed ✅"))
                    os.execl(sys.executable, sys.executable, *sys.argv)
                    return
                
                if count:
                    if mcount:
                        if media_type(message) == type or type == 'All':
                            try:
                                if media_type(message) == 'Document':
                                    doc_name = getattr(message.document, 'file_name', 'Unknown')
                                    caption = message.caption if Config.ENABLE_CAPTION else doc_name
                                    await user_client.send_document(tochat, message.document.file_id, caption=caption)
                                    try:
                                        if len(str(doc_name)) <= 95:
                                            print("Successfully forwarded: " + str(doc_name))
                                        else:
                                            logmsg = str(doc_name)
                                            logmsg = logmsg[:95] + "..."
                                            print("Successfully forwarded: " + logmsg)
                                    except:
                                        print("Unable to retrieve data.")
                                else:
                                    await user_client.forward_messages(tochat, fromchat, message.id)
                                    try:
                                        msg_text = message.text or message.caption or ""
                                        if len(str(msg_text)) == 0:
                                            logmsg = media_type(message)
                                        elif len(str(msg_text)) <= 95:
                                            logmsg = str(msg_text)
                                        else:
                                            logmsg = str(msg_text)
                                            logmsg = logmsg[:95] + "..."
                                        print("Successfully forwarded: " + logmsg)
                                    except:
                                        print("Unable to retrieve data.")
                                
                                status.add("1")
                                try:
                                    status.remove("2")
                                except:
                                    pass
                                
                                last_message_id = message.id
                                await asyncio.sleep(random.randint(2, 3))
                                mcount -= 1
                                count -= 1
                                MessageCount += 1
                                
                                # Update status message every 5 seconds
                                current_time = datetime.datetime.now()
                                if (current_time - last_status_update).total_seconds() >= 5:
                                    status_message = await format_status_message(MessageCount, start, type)
                                    await m.edit(status_message)
                                    last_status_update = current_time
                            except Exception as e:
                                error_msg = f"Error occurred: {str(e)}"
                                print(error_msg)
                                await m.edit(f"{await format_status_message(MessageCount, start, 'Error ❌')}\n\n{error_msg}")
                                os.execl(sys.executable, sys.executable, *sys.argv)
                                return
                    else:
                        print(f"You have sent {MessageCount} messages")
                        status.add("2")
                        status.remove("1")
                        sleep_time = random.randint(65, 132)
                        end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                        await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                        await asyncio.sleep(sleep_time)
                        mcount = random.randint(86, 98)
                else:
                    print(f"You have sent {MessageCount} messages")
                    status.add("2")
                    status.remove("1")
                    sleep_time = random.randint(968, 996)
                    end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                    await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                    await asyncio.sleep(sleep_time)
                    count = random.randint(468, 517)
                message_id += 1
        else:
            # Start from the specified message ID and iterate forward
            message_id = int(offsetid)
            while True:
                try:
                    message = await user_client.get_messages(fromchat, message_id)
                    if not message:
                        break
                except:
                    break
                # Process message here
                if message_limit != "0" and MessageCount >= int(message_limit):
                    status.add("3")
                    status.remove("1")
                    await m.edit(await format_status_message(MessageCount, start, "Completed ✅"))
                    os.execl(sys.executable, sys.executable, *sys.argv)
                    return
                
                if count:
                    if mcount:
                        if media_type(message) == type or type == 'All':
                            try:
                                if media_type(message) == 'Document':
                                    doc_name = getattr(message.document, 'file_name', 'Unknown')
                                    caption = message.caption if Config.ENABLE_CAPTION else doc_name
                                    await user_client.send_document(tochat, message.document.file_id, caption=caption)
                                    try:
                                        if len(str(doc_name)) <= 95:
                                            print("Successfully forwarded: " + str(doc_name))
                                        else:
                                            logmsg = str(doc_name)
                                            logmsg = logmsg[:95] + "..."
                                            print("Successfully forwarded: " + logmsg)
                                    except:
                                        print("Unable to retrieve data.")
                                else:
                                    await user_client.forward_messages(tochat, fromchat, message.id)
                                    try:
                                        msg_text = message.text or message.caption or ""
                                        if len(str(msg_text)) == 0:
                                            logmsg = media_type(message)
                                        elif len(str(msg_text)) <= 95:
                                            logmsg = str(msg_text)
                                        else:
                                            logmsg = str(msg_text)
                                            logmsg = logmsg[:95] + "..."
                                        print("Successfully forwarded: " + logmsg)
                                    except:
                                        print("Unable to retrieve data.")
                                
                                status.add("1")
                                try:
                                    status.remove("2")
                                except:
                                    pass
                                
                                last_message_id = message.id
                                await asyncio.sleep(random.randint(2, 3))
                                mcount -= 1
                                count -= 1
                                MessageCount += 1
                                
                                # Update status message every 5 seconds
                                current_time = datetime.datetime.now()
                                if (current_time - last_status_update).total_seconds() >= 5:
                                    status_message = await format_status_message(MessageCount, start, type)
                                    await m.edit(status_message)
                                    last_status_update = current_time
                            except Exception as e:
                                error_msg = f"Error occurred: {str(e)}"
                                print(error_msg)
                                await m.edit(f"{await format_status_message(MessageCount, start, 'Error ❌')}\n\n{error_msg}")
                                os.execl(sys.executable, sys.executable, *sys.argv)
                                return
                    else:
                        print(f"You have sent {MessageCount} messages")
                        status.add("2")
                        status.remove("1")
                        sleep_time = random.randint(65, 132)
                        end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                        await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                        await asyncio.sleep(sleep_time)
                        mcount = random.randint(86, 98)
                else:
                    print(f"You have sent {MessageCount} messages")
                    status.add("2")
                    status.remove("1")
                    sleep_time = random.randint(968, 996)
                    end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                    await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                    await asyncio.sleep(sleep_time)
                    count = random.randint(468, 517)
                message_id += 1
        os.execl(sys.executable, sys.executable, *sys.argv)
                
    except Exception as e:
            error_msg = f"Error occurred: {str(e)}"
            print(error_msg)
            await m.edit(f"Error: {error_msg}")
            os.execl(sys.executable, sys.executable, *sys.argv)
            return
