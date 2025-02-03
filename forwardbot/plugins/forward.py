from telethon.sync import events
from forwardbot import bot
from forwardbot import client
from forwardbot.utils import is_sudo
from forwardbot.tool import *
from telethon import Button
import asyncio
from forwardbot.utils import forwardbot_cmd
import datetime
from datetime import timedelta
import random
import sys
import os

MessageCount = 0
BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'

start = None
last_message_id = None
message_limit = 0

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

⚡ **Status**: {('Forwarding' if current_type == 'Document' else current_type)}
"""

    return status_message

# ❌ Use /cancel to stop forwarding
#  ⚡ **Status**: {'Active' if '1' in status else 'Sleeping' if '2' in status else 'Completed' if '3' in status else 'Idle' }

@forwardbot_cmd("forward", is_args=False)
async def handler(event):
    if not await is_sudo(event):
        await event.respond("You are not authorized to use this Bot. Create your own.")
        return
    if "1" in status:
        await event.respond("A task is already running.")
        return
    if "2" in status:
        await event.respond("Sleeping the engine for avoiding ban.")
        return
    if "3" in status:
        await event.respond("The task is completed.")
        return
    async with bot.conversation(event.chat_id) as conv:
        await conv.send_message("Please send the channel id from where you want to forward messages as a reply to this message.")
        while True:
            r = conv.wait_event(events.NewMessage(chats=event.chat_id))
            r = await r
            global fromchannel
            fromchannel = r.message.message.strip()
            if not r.is_reply:
                await conv.send_message("Please send the message as a reply to the message.")
            else:
                break
            
        await conv.send_message("Select how many messages you want to forward, 0 for unlimited")
        while True:
            r = conv.wait_event(events.NewMessage(chats=event.chat_id))
            r = await r
            global message_limit
            message_limit = r.message.message.strip()
            if not r.is_reply:
                await conv.send_message("Please send the message as a reply to the message.")
            else:
                break
        
        # Wait for button response
        #        await conv.send_message("Select how many messages you want to forward:", buttons=[
        #     [Button.inline('1000', b'1000'), Button.inline('3000', b'3000')],
        #     [Button.inline('5000', b'5000'), Button.inline('7000', b'7000')]
        # ])
               
        # resp = await conv.wait_event(events.CallbackQuery)
        # global message_limit
        # message_limit = int(resp.data.decode())
        # await resp.answer()
        
        while True:
            await conv.send_message("Okay now send me the message id from where you want to start forwarding as a reply to this message.(0 if you want to forward from beginning)")
            break
        while True:
            q = conv.wait_event(events.NewMessage(chats=event.chat_id))
            q = await q
            global offsetid
            offsetid = q.message.message.strip()
            if not q.is_reply:
                await conv.send_message("Please send the message as a reply to the message.")
            else:
                break
        await event.respond('Select What you need to forward', buttons=[
            [Button.inline('All Messages', b'all'), Button.inline('Only Photos', b'photo')],
            [Button.inline('Only Documents', b'docs'), Button.inline('Only Video', b'video')]
        ])

# @forwardbot_cmd("reset", is_args=False)
# async def handler(event):
#     if not await is_sudo(event):
#         await event.respond("You are not authorized to use this Bot. Create your own.")
#         return
#     global MessageCount, last_message_id
#     MessageCount = 0
#     last_message_id = None
#     await event.respond("Message count has been reset to 0")
#     print("Message count has been reset to 0")

# @forwardbot_cmd("uptime", is_args=False)
# async def handler(event):
#     if not await is_sudo(event):
#         await event.respond("You are not authorized to use this Bot. Create your own.")
#         return
#     global start
#     if start:
#         status_message = await format_status_message(MessageCount, start, "None")
#         await event.respond(status_message)
#     else:
#         await event.respond("Please start a forwarding to check the uptime")

@forwardbot_cmd("status", is_args=False)
async def handler(event):
    if not await is_sudo(event):
        await event.respond("You are not authorized to use this Bot. Create your own.")
        return
    
    if start:
        status_message = await format_status_message(MessageCount, start, "Current")
        await event.respond(status_message)
    else:
        current_status = "Running" if "1" in status else "Sleeping" if "2" in status else "Completed" if "3" in status else "Idle"
        await event.respond(f"Bot Status: {current_status}")

# @forwardbot_cmd("count", is_args=False)
# async def handler(event):
#     if not await is_sudo(event):
#         await event.respond("You are not authorized to use this Bot. Create your own.")
#         return
#     status_message = await format_status_message(MessageCount, start, "None")
#     await event.respond(status_message)

@bot.on(events.CallbackQuery)
async def handler(event):
    if event.data == b'all':
        type = "All"
        await event.delete()
    if event.data == b'docs':
        type = "Document"
        await event.delete()
    if event.data == b'photo':
        type = "Photo"
        await event.delete()
    if event.data == b'video':
        type = "Video"
        await event.delete()
    if type:
        if not await is_sudo(event):
            await event.respond("You are not authorized to use this Bot. Create your own.")
            return
        if "1" in status:
            await event.respond("A task is already running.")
            return
        if "2" in status:
            await event.respond("Sleeping the engine for avoiding ban.")
            return
        if "3" in status:
            await event.respond("The task is completed.")
            return
        try:
            m = await event.respond("Initializing forwarding...")
            fromchat = int(fromchannel)
            tochat = int("-1002332846289")
            count = random.randint(968, 1315)
            mcount = random.randint(151, 216)
            global MessageCount, start, last_message_id
            offset = int(offsetid)
            if offset:
                offset = offset-1
            print("Starting to forward")
            start = str(datetime.datetime.now())
            last_status_update = datetime.datetime.now()

            async for message in client.iter_messages(fromchat, reverse=True, offset_id=offset):
                if message_limit != "0" and MessageCount >= int(message_limit):
                    status.add("3")
                    status.remove("1")
                    await m.edit(await format_status_message(MessageCount, start, "Completed ✅"))
                    client.disconnect()
                    os.execl(sys.executable, sys.executable, *sys.argv)
                    return
                
                if count:
                    if mcount:
                        if media_type(message) == type or type == 'All':
                            try:
                                if media_type(message) == 'Document':
                                    await client.send_file(tochat, message.document)
                                    try:
                                        if len(str(message.file.name)) <= 95:
                                            print("Successfully forwarded: " + str(message.file.name))
                                        else:
                                            logmsg = str(message.file.name)
                                            logmsg = logmsg[:95] + "..."
                                            print("Successfully forwarded: " + logmsg)
                                    except:
                                        print("Unable to retrieve data.")
                                else:
                                    await client.send_message(tochat, message)
                                    try:
                                        if len(str(message.message)) == 0:
                                            logmsg = media_type(message)
                                        elif len(str(message.message)) <= 95:
                                            logmsg = str(message.message)
                                        else:
                                            logmsg = str(message.message)
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
                            except:
                                pass
                    else:
                        print(f"You have sent {MessageCount} messages")
                        status.add("2")
                        status.remove("1")
                        sleep_time = random.randint(40, 70)
                        end_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                        await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                        await asyncio.sleep(sleep_time)
                        mcount = random.randint(151, 216)
                else:
                    print(f"You have sent {MessageCount} messages")
                    status.add("2")
                    status.remove("1")
                    sleep_time = random.randint(1200, 1350)
                    end_time = (datetime.datetime.now() + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                    await m.edit(await format_status_message(MessageCount, start, f" Sleeping till {end_time}"))
                    await asyncio.sleep(sleep_time)
                    count = random.randint(968, 1315)
                    
        except ValueError:
            await m.edit("You must join the channel before starting forwarding.")
            return

        final_status = await format_status_message(MessageCount, start, f"{type} (Completed)")
        await event.respond(final_status)
        try:
            status.remove("1")
        except:
            pass
        try:
            status.remove("2")
        except:
            pass