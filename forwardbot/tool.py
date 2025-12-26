def media_type(message):
    """
    Get media type from Pyrogram message.
    
    Args:
        message: Pyrogram Message object
    
    Returns:
        str: Media type name or None if no media
    """
    if not message:
        return None
        
    if message.photo:
        return "Photo"
    if message.audio:
        return "Audio"
    if message.voice:
        return "Voice"
    if message.video_note:
        return "Round Video"
    if message.animation:
        return "Animation"
    if message.sticker:
        return "Sticker"
    if message.video:
        return "Video"
    if message.document:
        return "Document"
    
    return None
