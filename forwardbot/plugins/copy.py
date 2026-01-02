from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from pyrogram.errors import FloodWait
from forwardbot import bot, client, pending_conversations, Config
from forwardbot.utils import is_sudo
from forwardbot.tool import *
import asyncio
import datetime
from datetime import timedelta
import random
import sys
import os
import pytz
import tempfile
import time

# Handler to catch messages for listen pattern
@bot.on_message(filters.text & filters.private & ~filters.command(["start", "help", "forward", "copy", "status", "cancel", "autocopy"]))
async def catch_message(client, message):
    """Catch messages for listen pattern"""
    chat_id = message.chat.id
    if chat_id in pending_conversations:
        future = pending_conversations.pop(chat_id)
        if not future.done():
            future.set_result(message)

@bot.on_message(filters.command("autocopy"))
async def autocopy_command(client_bot, message):
    """Auto copy specific message: -1001776742853, message 804256"""
    if not await is_sudo(message):
        await message.reply("You are not authorized to use this Bot. Create your own.")
        return
    
    try:
        # Pre-configured values
        fromchat = -1001776742853  # Channel ID
        tochat = -1002332846289  # Destination
        message_id_to_copy = 797141
        
        m = await message.reply("Starting auto-copy from private channel...")
        
        # Step 1: Ensure source channel is accessible
        try:
            await m.edit("🔍 Accessing source channel...")
            
            # Try direct access first
            try:
                source_message = await client.get_messages(fromchat, message_id_to_copy)
                
                if not source_message:
                    await m.edit("❌ Message not found or inaccessible.")
                    return
                    
            except Exception as msg_error:
                error_str = str(msg_error)
                
                # If CHANNEL_INVALID, try to iterate dialogs to find the channel
                if "CHANNEL_INVALID" in error_str or "Peer id invalid" in error_str:
                    await m.edit("⚠️ Source channel not in cache, scanning dialogs...\nThis may take a moment.")
                    
                    found = False
                    async for dialog in client.get_dialogs(limit=None):
                        if dialog.chat.id == fromchat:
                            found = True
                            await m.edit(f"✅ Found source: {dialog.chat.title}")
                            break
                    
                    if not found:
                        await m.edit(f"❌ Source channel {fromchat} not found.\n\n"
                                   f"Make sure you've joined it with your user account.")
                        return
                    
                    # Try getting message again after finding channel
                    source_message = await client.get_messages(fromchat, message_id_to_copy)
                    if not source_message:
                        await m.edit("❌ Message not found after channel scan.")
                        return
                else:
                    raise msg_error
        
        except Exception as e:
            error_msg = str(e)
            await m.edit(f"❌ Error accessing source: {error_msg}\n\n"
                       f"Open the channel in Telegram and try again.")
            return
        
        # Step 2: Ensure destination channel is accessible
        try:
            await m.edit("🔍 Accessing destination channel...")
            
            # Try to get chat info to add to cache
            try:
                dest_chat = await client.get_chat(tochat)
                await m.edit(f"✅ Destination: {dest_chat.title}")
            except Exception as dest_error:
                error_str = str(dest_error)
                
                if "CHANNEL_INVALID" in error_str or "Peer id invalid" in error_str:
                    await m.edit("⚠️ Destination not in cache, scanning dialogs...")
                    
                    found = False
                    async for dialog in client.get_dialogs(limit=None):
                        if dialog.chat.id == tochat:
                            found = True
                            await m.edit(f"✅ Found destination: {dialog.chat.title}")
                            break
                    
                    if not found:
                        await m.edit(f"❌ Destination channel {tochat} not found.\n\n"
                                   f"Make sure you've joined it with your user account.")
                        return
                else:
                    raise dest_error
                    
        except Exception as e:
            error_msg = str(e)
            await m.edit(f"❌ Error accessing destination: {error_msg}\n\n"
                       f"Join the destination channel and try again.")
            return
        
        # Step 3: Download and upload the document
        if source_message.document:
            await m.edit("⬇️ Downloading document...")
            
            # Set filename for progress callback
            global current_file_name
            current_file_name = source_message.document.file_name if source_message.document.file_name else "Document"
            
            # Download the file with progress
            progress_message = m
            progress_start_time = None
            
            file_path = await source_message.download(
                file_name=tempfile.gettempdir() + "/",
                progress=download_progress_callback
            )
            
            if file_path:
                await m.edit("⬆️ Uploading document...")
                
                # Reset for upload
                progress_start_time = None
                
                # Get caption
                caption = current_file_name
                
                # Upload to destination
                sent_message = await client.send_document(
                    tochat,
                    file_path,
                    caption=caption,
                    progress=upload_progress_callback
                )
                
                # Clean up
                try:
                    if os.path.exists(file_path):
                        os.remove(file_path)
                except:
                    pass
                
                # Get file size
                file_size = source_message.document.file_size if source_message.document else 0
                if file_size > 0:
                    if file_size < 1024 * 1024:
                        size_str = f"{file_size/1024:.2f} KB"
                    else:
                        size_str = f"{file_size/(1024*1024):.2f} MB"
                else:
                    size_str = "Unknown"
                
                # Get title
                title = source_message.document.file_name if source_message.document and source_message.document.file_name else "Document"
                
                # Create channel link
                channel_id = str(tochat).replace("-100", "")
                message_link = f"https://t.me/c/{channel_id}/{sent_message.id}"
                
                success_msg = f"""✅ Document copied successfully!

📹 {title}
💾 Size: {size_str}

🔗 Open in Channel ({message_link})"""
                
                await m.edit(success_msg)
            else:
                await m.edit("❌ Failed to download the file.")
        else:
            await m.edit("❌ No document found in that message.")
            
    except Exception as e:
        error_msg = f"Error: {str(e)}"
        print(error_msg)
        await message.reply(f"❌ {error_msg}\n\nMake sure you have joined the channel and the message ID is correct.")

MessageCount = 0
BOT_STATUS = "0"
status = set(int(x) for x in (BOT_STATUS).split())
datetimeFormat = '%Y-%m-%d %H:%M:%S.%f'

start = None
last_message_id = None
message_limit = 0
ist = pytz.timezone('Asia/Kolkata')

# Global variables for file progress tracking
current_file_progress = {"downloaded": 0, "total": 0, "percentage": 0}
current_file_name = "Unknown"
progress_message = None
progress_start_time = None
last_progress_update = None

# File size limits
MAX_FILE_SIZE = 2 * 1024 * 1024 * 1024  # 2GB in bytes
SPLIT_CHUNK_SIZE = int(1.95 * 1024 * 1024 * 1024)  # 1.95GB per chunk

def format_bytes(bytes_size):
    """Format bytes to human readable format"""
    if bytes_size < 1024:
        return f"{bytes_size}B"
    elif bytes_size < 1024 * 1024:
        return f"{bytes_size/1024:.1f}KB"
    elif bytes_size < 1024 * 1024 * 1024:
        return f"{bytes_size/(1024*1024):.2f}MB"
    else:
        return f"{bytes_size/(1024*1024*1024):.2f}GB"

def create_progress_bar(percentage, length=20):
    """Create a visual progress bar"""
    filled = int(length * percentage / 100)
    empty = length - filled
    return f"[{'█' * filled}{'░' * empty}]"

def split_file(file_path, chunk_size=SPLIT_CHUNK_SIZE):
    """
    Split a large file into chunks.
    
    Args:
        file_path: Path to the file to split
        chunk_size: Size of each chunk in bytes (default 1.95GB)
    
    Returns:
        List of chunk file paths
    """
    file_size = os.path.getsize(file_path)
    
    if file_size <= MAX_FILE_SIZE:
        # File is small enough, no splitting needed
        return [file_path]
    
    # Calculate number of parts needed
    num_parts = (file_size + chunk_size - 1) // chunk_size
    
    chunk_files = []
    base_name = os.path.basename(file_path)
    file_name, file_ext = os.path.splitext(base_name)
    
    print(f"Splitting file {base_name} ({format_bytes(file_size)}) into {num_parts} parts...")
    
    with open(file_path, 'rb') as source_file:
        for part_num in range(num_parts):
            # Create chunk filename
            chunk_filename = f"{file_name}.part{part_num + 1:03d}{file_ext}"
            chunk_path = os.path.join(os.path.dirname(file_path), chunk_filename)
            
            # Read and write chunk
            bytes_to_read = min(chunk_size, file_size - (part_num * chunk_size))
            
            with open(chunk_path, 'wb') as chunk_file:
                bytes_written = 0
                while bytes_written < bytes_to_read:
                    # Read in smaller blocks for memory efficiency
                    block_size = min(8192, bytes_to_read - bytes_written)
                    data = source_file.read(block_size)
                    if not data:
                        break
                    chunk_file.write(data)
                    bytes_written += len(data)
            
            chunk_files.append(chunk_path)
            print(f"Created chunk {part_num + 1}/{num_parts}: {chunk_filename} ({format_bytes(bytes_written)})")
    
    return chunk_files

async def download_progress_callback(current, total):
    """Callback for download progress"""
    global current_file_progress, current_file_name, progress_message, progress_start_time, last_progress_update
    
    # Initialize start time on first call
    if progress_start_time is None:
        progress_start_time = time.time()
        last_progress_update = time.time()
    
    percentage = (current / total) * 100 if total > 0 else 0
    current_file_progress = {
        "downloaded": current,
        "total": total,
        "percentage": percentage
    }
    
    # Calculate speed and ETA
    elapsed_time = time.time() - progress_start_time
    speed = current / elapsed_time if elapsed_time > 0 else 0
    remaining_bytes = total - current
    eta_seconds = remaining_bytes / speed if speed > 0 else 0
    
    # Format speed
    if speed < 1024:
        speed_str = f"{speed:.1f}B/s"
    elif speed < 1024 * 1024:
        speed_str = f"{speed/1024:.1f}KB/s"
    else:
        speed_str = f"{speed/(1024*1024):.2f}MB/s"
    
    # Format ETA
    if eta_seconds < 60:
        eta_str = f"{int(eta_seconds)}s"
    elif eta_seconds < 3600:
        eta_str = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
    else:
        eta_str = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
    
    # Update message every 5 seconds or when complete
    current_time = time.time()
    should_update = (
        (current_time - last_progress_update >= 5) or 
        (current == total)
    )
    
    if progress_message and should_update:
        try:
            progress_bar = create_progress_bar(percentage, 20)
            progress_text = f"""
⬇️ **Downloading File**
📄 **{current_file_name}**

{progress_bar} {percentage:.1f}%

📥 **Downloaded**: {format_bytes(current)} / {format_bytes(total)}
⚡ **Remaining**: {format_bytes(remaining_bytes)}
🚀 **Speed**: {speed_str}
⏱️ **ETA**: {eta_str}
"""
            await progress_message.edit(progress_text)
            last_progress_update = current_time
        except Exception as e:
            # Ignore edit errors (too many requests, etc.)
            pass

async def upload_progress_callback(current, total):
    """Callback for upload progress"""
    global current_file_progress, current_file_name, progress_message, progress_start_time, last_progress_update
    
    # Reset start time for upload
    if current == 0 or progress_start_time is None:
        progress_start_time = time.time()
        last_progress_update = time.time()
    
    percentage = (current / total) * 100 if total > 0 else 0
    current_file_progress = {
        "uploaded": current,
        "total": total,
        "percentage": percentage
    }
    
    # Calculate speed and ETA
    elapsed_time = time.time() - progress_start_time
    speed = current / elapsed_time if elapsed_time > 0 else 0
    remaining_bytes = total - current
    eta_seconds = remaining_bytes / speed if speed > 0 else 0
    
    # Format speed
    if speed < 1024:
        speed_str = f"{speed:.1f}B/s"
    elif speed < 1024 * 1024:
        speed_str = f"{speed/1024:.1f}KB/s"
    else:
        speed_str = f"{speed/(1024*1024):.2f}MB/s"
    
    # Format ETA
    if eta_seconds < 60:
        eta_str = f"{int(eta_seconds)}s"
    elif eta_seconds < 3600:
        eta_str = f"{int(eta_seconds/60)}m {int(eta_seconds%60)}s"
    else:
        eta_str = f"{int(eta_seconds/3600)}h {int((eta_seconds%3600)/60)}m"
    
    # Update message every 5 seconds or when complete
    current_time = time.time()
    should_update = (
        (current_time - last_progress_update >= 5) or 
        (current == total)
    )
    
    if progress_message and should_update:
        try:
            progress_bar = create_progress_bar(percentage, 20)
            progress_text = f"""
⬆️ **Uploading File**
📄 **{current_file_name}**

{progress_bar} {percentage:.1f}%

📤 **Uploaded**: {format_bytes(current)} / {format_bytes(total)}
⚡ **Remaining**: {format_bytes(remaining_bytes)}
🚀 **Speed**: {speed_str}
⏱️ **ETA**: {eta_str}
"""
            await progress_message.edit(progress_text)
            last_progress_update = current_time
        except Exception as e:
            # Ignore edit errors (too many requests, etc.)
            pass

async def format_status_message(message_count, start_time, current_type, current_action=None, progress_info=None):
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
    
    # Calculate speed and ETA if we have message limit
    speed_info = ""
    eta_info = ""
    progress_bar = ""
    
    if start_time and message_count > 0:
        elapsed_seconds = (current_time - datetime.datetime.strptime(start_time, datetimeFormat)).total_seconds()
        if elapsed_seconds > 0:
            messages_per_second = message_count / elapsed_seconds
            messages_per_minute = messages_per_second * 60
            speed_info = f"⚡ **Speed**: {messages_per_minute:.1f} msg/min"
            
            # Calculate ETA if we have a limit
            if message_limit and message_limit != "0":
                remaining = int(message_limit) - message_count
                if remaining > 0 and messages_per_second > 0:
                    eta_seconds = remaining / messages_per_second
                    eta_minutes = int(eta_seconds / 60)
                    eta_hours = int(eta_minutes / 60)
                    eta_minutes = eta_minutes % 60
                    
                    if eta_hours > 0:
                        eta_info = f"⏳ **ETA**: ~{eta_hours}h {eta_minutes}m"
                    else:
                        eta_info = f"⏳ **ETA**: ~{eta_minutes}m"
                
                # Progress bar
                progress_percent = (message_count / int(message_limit)) * 100
                filled = int(progress_percent / 10)
                empty = 10 - filled
                progress_bar = f"📊 **Progress**: [{'█' * filled}{'░' * empty}] {progress_percent:.1f}%\n"
    
    # Current action info (downloading/uploading)
    action_info = ""
    if current_action:
        action_info = f"🔄 **Current**: {current_action}\n"
    
    # Progress info (file size, etc.)
    progress_detail = ""
    if progress_info:
        progress_detail = f"📦 **File**: {progress_info}\n"
    
    status_message = f"""📊 **Copy Bot Status** (Protected Mode)
    
⏱ **Uptime**: {days}d {hours}h {minutes}m {seconds}s
📤 **Total Copied**: {message_count} messages
{progress_bar}📝 **Last Message ID**: `{last_message_id or 'None'}`
🔍 **Channel ID**: `{fromchannel or 'None'}`
{speed_info}
{eta_info}

{action_info}{progress_detail}⚡ **Status**: {('Copying' if current_type in ['Document', 'Photo', 'Video', 'All'] else current_type)}
"""

    return status_message

@bot.on_message(filters.command("copy"))
async def copy_command(bot_client, message):
    """
    Copy messages from protected/restricted channels using download-upload method.
    This bypasses forward restrictions by downloading and re-uploading content.
    """
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
    await message.reply("Please send the channel id from where you want to copy messages.")
    response = await bot_client.listen(message.chat.id)
    global fromchannel
    fromchannel = response.text.strip()
    
    # Step 2: Ask for message limit
    await message.reply("Select how many messages you want to copy, 0 for unlimited")
    response = await bot_client.listen(message.chat.id)
    global message_limit
    message_limit = response.text.strip()
    
    # Step 3: Ask for offset
    await message.reply("Okay now send me the message id from where you want to start copying (0 if you want to copy from beginning)")
    response = await bot_client.listen(message.chat.id)
    global offsetid
    offsetid = response.text.strip()
    
    # Step 4: Show buttons
    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('All Messages', callback_data='copy_all'),
            InlineKeyboardButton('Only Photos', callback_data='copy_photo')
        ],
        [
            InlineKeyboardButton('Only Documents', callback_data='copy_docs'),
            InlineKeyboardButton('Only Video', callback_data='copy_video')
        ]
    ])
    await message.reply('Select What you need to copy', reply_markup=keyboard)

@bot.on_callback_query(filters.regex(r'^copy_'))
async def copy_handler(client, callback_query):
    """Handle copy button callbacks for protected channel copying"""
    
    global MessageCount, start, last_message_id, progress_message, progress_start_time, current_file_name
    
    # Determine type based on callback data
    if callback_query.data == 'copy_all':
        type = "All"
        await callback_query.message.delete()
    elif callback_query.data == 'copy_docs':
        type = "Document"
        await callback_query.message.delete()
    elif callback_query.data == 'copy_photo':
        type = "Photo"
        await callback_query.message.delete()
    elif callback_query.data == 'copy_video':
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
    
    from forwardbot import client as user_client
    try:
        m = await callback_query.message.reply("Initializing copying from protected channel...")
        # Try to parse as integer, if fails use as username
        try:
            fromchat = int(fromchannel)
        except ValueError:
            fromchat = fromchannel
        tochat = int("-1002332846289")
        # Ensure source channel is accessible
        try:
            await m.edit("🔍 Accessing source channel...")
            chat_info = await user_client.get_chat(fromchat)
            await m.edit(f"✅ Source: {chat_info.title}")
        except Exception as source_error:
            error_str = str(source_error)
            if "CHANNEL_INVALID" in error_str or "Peer id invalid" in error_str:
                await m.edit("⚠️ Source not in cache, scanning dialogs...")
                found = False
                async for dialog in user_client.get_dialogs(limit=None):
                    if dialog.chat.id == fromchat:
                        found = True
                        await m.edit(f"✅ Found source: {dialog.chat.title}")
                        break
                if not found:
                    await m.edit(f"❌ Source channel not found. Join it first.")
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
                    await m.edit(f"❌ Destination channel not found. Join it first.")
                    return
            else:
                raise dest_error
        # Handle single message copy
        if message_limit == "1":
            try:
                source_message = await user_client.get_messages(fromchat, int(offsetid))
                if not source_message:
                    await m.edit("❌ Message not found or inaccessible.")
                    return
                
                # Step 3: Download and upload the document
                if source_message.document:
                    await m.edit("⬇️ Downloading document...")
                    
                    # Set filename for progress callback
                    current_file_name = source_message.document.file_name if source_message.document.file_name else "Document"
                    
                    # Download the file with progress
                    progress_message = m
                    progress_start_time = None
                    
                    file_path = await source_message.download(
                        file_name=tempfile.gettempdir() + "/",
                        progress=download_progress_callback
                    )
                    
                    if file_path:
                        await m.edit("⬆️ Uploading document...")
                        
                        # Reset for upload
                        progress_start_time = None
                        
                        # Get caption
                        caption = current_file_name
                        
                        # Upload to destination
                        sent_message = await user_client.send_document(
                            tochat,
                            file_path,
                            caption=caption,
                            progress=upload_progress_callback
                        )
                        
                        # Clean up
                        try:
                            if os.path.exists(file_path):
                                os.remove(file_path)
                        except:
                            pass
                        
                        # Get file size
                        file_size = source_message.document.file_size if source_message.document else 0
                        if file_size > 0:
                            if file_size < 1024 * 1024:
                                size_str = f"{file_size/1024:.2f} KB"
                            else:
                                size_str = f"{file_size/(1024*1024):.2f} MB"
                        else:
                            size_str = "Unknown"
                        
                        # Get title
                        title = source_message.document.file_name if source_message.document and source_message.document.file_name else "Document"
                        
                        # Create channel link
                        channel_id = str(tochat).replace("-100", "")
                        message_link = f"https://t.me/c/{channel_id}/{sent_message.id}"
                        
                        success_msg = f"""✅ Document copied successfully!

📹 {title}
💾 Size: {size_str}

🔗 Open in Channel ({message_link})"""
                        
                        await m.edit(success_msg)
                        MessageCount += 1
                        return
                    else:
                        await m.edit("❌ Failed to download the file.")
                        return
                else:
                    await m.edit("❌ No document found in that message.")
                    return
                    
            except Exception as e:
                error_msg = str(e)
                await m.edit(f"❌ Error: {error_msg}")
                return
        
        # Proceed with multiple message copy
        # Increased limits to reduce frequency and avoid bans
        count = random.randint(350, 420)  # Reduced from 468-517
        mcount = random.randint(50, 70)   # Reduced from 86-98
        MessageCount, start, last_message_id
        print("Starting to copy from protected channel")
        start = str(datetime.datetime.now())
        last_status_update = datetime.datetime.now()
        await m.edit("🚀 Starting copy process...")
        await asyncio.sleep(1)
        if offsetid == "0":
            message_id = 1
            while True:
                try:
                    message = await user_client.get_messages(fromchat, message_id)
                    if not message:
                        break
                except:
                    break
            if message_limit != "0" and MessageCount >= int(message_limit):
                status.add("3")
                try:
                    status.remove("1")
                except:
                    pass
                limit_reached_msg = await format_status_message(
                    MessageCount, 
                    start, 
                    "✅ Completed",
                    current_action=f"🎯 Message limit reached ({message_limit} messages)"
                )
                await m.edit(limit_reached_msg)
                os.execl(sys.executable, sys.executable, *sys.argv)
                return
            
            if count:
                if mcount:
                    if media_type(message) == type or type == 'All':
                        try:
                            # Download and re-upload method for protected content
                            temp_file = None
                            
                            if message.media:
                                # Get file info - Pyrogram way
                                file_name = "Unknown"
                                file_size = 0
                                
                                try:
                                    # Get media object
                                    media = message.document or message.video or message.audio or message.photo or message.voice or message.animation
                                    if media:
                                        file_name = getattr(media, 'file_name', None) or f"{media_type(message)}"
                                        file_size = getattr(media, 'file_size', 0) or 0
                                except:
                                    pass
                                
                                # Format file size
                                if file_size > 0:
                                    if file_size < 1024:
                                        size_str = f"{file_size}B"
                                    elif file_size < 1024 * 1024:
                                        size_str = f"{file_size/1024:.1f}KB"
                                    elif file_size < 1024 * 1024 * 1024:
                                        size_str = f"{file_size/(1024*1024):.1f}MB"
                                    else:
                                        size_str = f"{file_size/(1024*1024*1024):.2f}GB"
                                    
                                    progress_info = f"{file_name[:30]} ({size_str})"
                                else:
                                    progress_info = f"{file_name[:30]}"
                                
                                # Update status - Downloading
                                print(f"Downloading message {message.id}...")
                                
                                # Set global variables for progress callbacks
                                current_file_name = file_name[:50]  # Limit filename length
                                progress_message = m
                                progress_start_time = None  # Reset for new download
                                
                                # Create initial progress message
                                initial_progress = f"""
⬇️ **Downloading File**

📦 **File**: {file_name[:40]}
📏 **Size**: {format_bytes(file_size)}
🆔 **Message ID**: {message.id}

{create_progress_bar(0, 20)} 0.0%

📥 Downloaded: 0B / {format_bytes(file_size)}
⚡ Starting download...
"""
                                await m.edit(initial_progress)
                                
                                # Download media to temporary location with progress callback
                                temp_file = await message.download(
                                    file_name=tempfile.gettempdir() + "/",
                                    progress=download_progress_callback
                                )
                                
                                if temp_file:
                                    # Get caption if exists
                                    caption = message.caption if message.caption else (message.text if message.text else "")
                                    
                                    # Update status - Uploading
                                    print(f"Uploading to destination...")
                                    
                                    # Reset progress timer for upload
                                    progress_start_time = None
                                    
                                    # Get file size for upload
                                    upload_size = os.path.getsize(temp_file) if os.path.exists(temp_file) else file_size
                                    
                                    # Check if file needs splitting
                                    if upload_size > MAX_FILE_SIZE:
                                        # File is larger than 2GB, need to split
                                        split_info = f"""
📦 **Large File Detected!**

📦 **File**: {file_name[:40]}
📏 **Size**: {format_bytes(upload_size)}
⚠️ **Action**: Splitting into parts (max 1.95GB each)

⏳ Splitting file...
"""
                                        await m.edit(split_info)
                                        
                                        # Split the file
                                        chunk_files = split_file(temp_file)
                                        num_parts = len(chunk_files)
                                        
                                        print(f"File split into {num_parts} parts")
                                        
                                        # Upload each chunk
                                        for part_num, chunk_file in enumerate(chunk_files, 1):
                                            chunk_size = os.path.getsize(chunk_file)
                                            chunk_name = os.path.basename(chunk_file)
                                            
                                            # Reset progress timer for each chunk
                                            progress_start_time = None
                                            
                                            # Create caption for this part
                                            part_caption = chunk_name
                                            
                                            # Create initial upload progress for this part
                                            initial_upload = f"""
⬆️ **Uploading Part {part_num}/{num_parts}**

📦 **File**: {chunk_name[:40]}
📏 **Size**: {format_bytes(chunk_size)}
🆔 **Message ID**: {message.id}

{create_progress_bar(0, 20)} 0.0%

📤 Uploaded: 0B / {format_bytes(chunk_size)}
⚡ Starting upload...
"""
                                            await m.edit(initial_upload)
                                            
                                            # Upload this chunk with progress callback
                                            await client.send_document(
                                                tochat, 
                                                chunk_file,
                                                caption=part_caption,
                                                progress=upload_progress_callback
                                            )
                                            
                                            print(f"Uploaded part {part_num}/{num_parts}: {chunk_name}")
                                            
                                            # Clean up this chunk file
                                            try:
                                                if os.path.exists(chunk_file):
                                                    os.remove(chunk_file)
                                                    print(f"Deleted chunk file: {chunk_name}")
                                            except Exception as e:
                                                print(f"Failed to delete chunk file {chunk_name}: {e}")
                                            
                                            # Small delay between parts
                                            if part_num < num_parts:
                                                await asyncio.sleep(2)
                                        
                                        # Clean up original temp file
                                        try:
                                            if os.path.exists(temp_file):
                                                os.remove(temp_file)
                                                print(f"Deleted original temp file")
                                        except Exception as e:
                                            print(f"Failed to delete original temp file: {e}")
                                        
                                        print(f"Successfully uploaded all {num_parts} parts")
                                    
                                    else:
                                        # File is small enough, upload normally
                                        # Create initial upload progress message
                                        initial_upload = f"""
⬆️ **Uploading File**

📦 **File**: {file_name[:40]}
📏 **Size**: {format_bytes(upload_size)}
🆔 **Message ID**: {message.id}

{create_progress_bar(0, 20)} 0.0%

📤 Uploaded: 0B / {format_bytes(upload_size)}
⚡ Starting upload...
"""
                                        await m.edit(initial_upload)
                                        
                                        # Re-upload to destination with progress callback
                                        if media_type(message) == 'Document':
                                            await client.send_document(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Video':
                                            await client.send_video(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Photo':
                                            await client.send_photo(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Audio':
                                            await client.send_audio(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Voice':
                                            await client.send_voice(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        else:
                                            await client.send_document(
                                                tochat, 
                                                temp_file,
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        
                                        # Clean up temporary file
                                        try:
                                            if os.path.exists(temp_file):
                                                os.remove(temp_file)
                                        except Exception as e:
                                            print(f"Failed to delete temp file: {e}")
                                    
                                    try:
                                        logmsg = caption[:95] + "..." if len(caption) > 95 else caption
                                        if not logmsg:
                                            logmsg = f"{media_type(message)} (ID: {message.id})"
                                        print(f"Successfully copied: {logmsg}")
                                    except:
                                        print(f"Successfully copied message {message.id}")
                                else:
                                    print(f"Failed to download message {message.id}")
                            
                            elif message.text:
                                # Text message - just send it
                                await client.send_message(tochat, message.text)
                                logmsg = message.text[:95] + "..." if len(message.text) > 95 else message.text
                                print(f"Successfully copied text: {logmsg}")
                            else:
                                # Skip empty messages
                                pass
                            
                            # Move counter updates AFTER successful sending
                            status.add("1")
                            try:
                                status.remove("2")
                            except:
                                pass
                            
                            last_message_id = message.id
                            # Increased delay to prevent flood bans (5-10 seconds)
                            await asyncio.sleep(random.randint(5, 10))
                            mcount -= 1
                            count -= 1
                            MessageCount += 1
                            
                            # Update status message every 5 seconds for more responsive updates
                            current_time = datetime.datetime.now()
                            if (current_time - last_status_update).total_seconds() >= 5:
                                status_message = await format_status_message(
                                    MessageCount, 
                                    start, 
                                    type,
                                    current_action="✅ Completed last message"
                                )
                                await m.edit(status_message)
                                last_status_update = current_time

                        except FloodWait as e:
                            # Telegram flood limit - wait the required time
                            wait_time = e.value
                            print(f"FloodWait: Waiting {wait_time} seconds")
                            end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=wait_time)).strftime("%I:%M %p")
                            flood_msg = await format_status_message(
                                MessageCount, 
                                start, 
                                f'⚠️ Flood limit hit!',
                                current_action=f"⏸️ Waiting till {end_time}"
                            )
                            await callback_query.message.reply(flood_msg)
                            await asyncio.sleep(wait_time)
                            # Continue without incrementing counters

                        except Exception as e:
                            error_msg = f"Error occurred: {str(e)}"
                            print(error_msg)
                            # Clean up temp file if exists
                            if temp_file and os.path.exists(temp_file):
                                try:
                                    os.remove(temp_file)
                                except:
                                    pass
                            # Continue to next message instead of crashing
                else:
                    print(f"You have copied {MessageCount} messages")
                    status.add("2")
                    try:
                        status.remove("1")
                    except:
                        pass
                    # Longer sleep between batches to avoid detection
                    sleep_time = random.randint(300, 480)  # 5-8 minutes
                    end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                    sleep_msg = await format_status_message(
                        MessageCount, 
                        start, 
                        "💤 Sleeping",
                        current_action=f"😴 Sleeping till {end_time} (ban prevention)"
                    )
                    await m.edit(sleep_msg)
                    await asyncio.sleep(sleep_time)
                    mcount = random.randint(50, 70)  # Reduced batch size
            else:
                print(f"You have copied {MessageCount} messages")
                status.add("2")
                try:
                    status.remove("1")
                except:
                    pass
                # Extended sleep between major batches (30-45 minutes)
                sleep_time = random.randint(1800, 2700)  # Increased from 1560-2050
                end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                sleep_msg = await format_status_message(
                    MessageCount, 
                    start, 
                    "💤 Long Sleep",
                    current_action=f"😴 Sleeping till {end_time} (ban prevention)"
                )
                await m.edit(sleep_msg)
                await asyncio.sleep(sleep_time)
                count = random.randint(350, 420)  # Reduced batch size
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
                    try:
                        status.remove("1")
                    except:
                        pass
                    limit_reached_msg = await format_status_message(
                        MessageCount, 
                        start, 
                        "✅ Completed",
                        current_action=f"🎯 Message limit reached ({message_limit} messages)"
                    )
                    await m.edit(limit_reached_msg)
                    os.execl(sys.executable, sys.executable, *sys.argv)
                    return
                
                if count:
                    if mcount:
                        if media_type(message) == type or type == 'All':
                            try:
                                # Download and re-upload method for protected content
                                temp_file = None
                                
                                if message.media:
                                    # Get file info - Pyrogram way
                                    file_name = "Unknown"
                                    file_size = 0
                                    
                                    try:
                                        # Get media object
                                        media = message.document or message.video or message.audio or message.photo or message.voice or message.animation
                                        if media:
                                            file_name = getattr(media, 'file_name', None) or f"{media_type(message)}"
                                            file_size = getattr(media, 'file_size', 0) or 0
                                    except:
                                        pass
                                    
                                    # Format file size
                                    if file_size > 0:
                                        if file_size < 1024:
                                            size_str = f"{file_size}B"
                                        elif file_size < 1024 * 1024:
                                            size_str = f"{file_size/1024:.1f}KB"
                                        elif file_size < 1024 * 1024 * 1024:
                                            size_str = f"{file_size/(1024*1024):.1f}MB"
                                        else:
                                            size_str = f"{file_size/(1024*1024*1024):.2f}GB"
                                        
                                        progress_info = f"{file_name[:30]} ({size_str})"
                                    else:
                                        progress_info = f"{file_name[:30]}"
                                    
                                    # Update status - Downloading
                                    print(f"Downloading message {message.id}...")
                                    
                                    # Set global progress message for callbacks
                                    progress_message = m
                                    progress_start_time = None  # Reset for new download
                                    
                                    # Create initial progress message
                                    initial_progress = f"""
⬇️ **Downloading File**

📦 **File**: {file_name[:40]}
📏 **Size**: {format_bytes(file_size)}
🆔 **Message ID**: {message.id}

{create_progress_bar(0, 20)} 0.0%

📥 Downloaded: 0B / {format_bytes(file_size)}
⚡ Starting download...
"""
                                    await m.edit(initial_progress)
                                    
                                    # Download media to temporary location with progress callback
                                    temp_file = await message.download(
                                        file_name=tempfile.gettempdir() + "/",
                                        progress=download_progress_callback
                                    )
                                    
                                    if temp_file:
                                        print(f"Downloaded to {temp_file}")
                                        
                                        # Update status - Uploading
                                        upload_progress = f"""
⬆️ **Uploading File**

📦 **File**: {file_name[:40]}
📏 **Size**: {format_bytes(file_size)}
🆔 **Message ID**: {message.id}

{create_progress_bar(0, 20)} 0.0%

📤 Uploaded: 0B / {format_bytes(file_size)}
⚡ Starting upload...
"""
                                        await m.edit(upload_progress)
                                        
                                        # Upload the file to destination with progress callback
                                        if media_type(message) == 'Document':
                                            uploaded_msg = await user_client.send_document(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Video':
                                            uploaded_msg = await user_client.send_video(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Audio':
                                            uploaded_msg = await user_client.send_audio(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Photo':
                                            uploaded_msg = await user_client.send_photo(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Voice':
                                            uploaded_msg = await user_client.send_voice(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        elif media_type(message) == 'Animation':
                                            uploaded_msg = await user_client.send_animation(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        else:
                                            # Fallback to document
                                            uploaded_msg = await user_client.send_document(
                                                tochat, 
                                                temp_file, 
                                                caption=file_name,
                                                progress=upload_progress_callback
                                            )
                                        
                                        print(f"Successfully copied: {file_name}")
                                        
                                        # Clean up temp file
                                        try:
                                            os.unlink(temp_file)
                                        except:
                                            pass
                                        
                                        status.add("1")
                                        try:
                                            status.remove("2")
                                        except:
                                            pass
                                        
                                        last_message_id = message.id
                                        # Increased delay to prevent flood bans (5-10 seconds)
                                        await asyncio.sleep(random.randint(5, 10))
                                        mcount -= 1
                                        count -= 1
                                        MessageCount += 1
                                        
                                        # Update status message every 5 seconds
                                        current_time = datetime.datetime.now()
                                        if (current_time - last_status_update).total_seconds() >= 5:
                                            status_message = await format_status_message(MessageCount, start, type)
                                            await m.edit(status_message)
                                            last_status_update = current_time
                                    else:
                                        print(f"Failed to download message {message.id}")
                                else:
                                    # For text messages or other non-media
                                    await user_client.send_message(tochat, message.text or message.caption or "")
                                    print("Successfully copied: Text message")
                                    
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
                            print(f"Skipping message {message.id} - type {media_type(message)} not selected")
                    else:
                        print(f"You have copied {MessageCount} messages")
                        status.add("2")
                        try:
                            status.remove("1")
                        except:
                            pass
                        sleep_time = random.randint(65, 132)
                        end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                        sleep_msg = await format_status_message(
                            MessageCount, 
                            start, 
                            "💤 Sleeping",
                            current_action=f"😴 Sleeping till {end_time}"
                        )
                        await m.edit(sleep_msg)
                        await asyncio.sleep(sleep_time)
                        mcount = random.randint(86, 98)
                else:
                    print(f"You have copied {MessageCount} messages")
                    status.add("2")
                    try:
                        status.remove("1")
                    except:
                        pass
                    sleep_time = random.randint(1560, 2050)
                    end_time = (datetime.datetime.now(ist) + datetime.timedelta(seconds=sleep_time)).strftime("%I:%M %p")
                    sleep_msg = await format_status_message(
                        MessageCount, 
                        start, 
                        "💤 Sleeping",
                        current_action=f"😴 Sleeping till {end_time}"
                    )
                    await m.edit(sleep_msg)
                    await asyncio.sleep(sleep_time)
                    count = random.randint(468, 517)
                message_id += 1
                
    except Exception as e:
        error_msg = f"Error occurred: {str(e)}"
        print(error_msg)
        await callback_query.message.reply(f"Error: {error_msg}\n\nMake sure you have joined the channel and have access to it.")
        os.execl(sys.executable, sys.executable, *sys.argv)
        return

