# Forward Bot

<p align="center"><a href="#"><img src="https://telegra.ph/file/fa4d9d23a211f6bcf807b.jpg" width="250"></a></p> 
<h1 align="center"><b>Forwarder Bot</b></h1>
<h4 align="center">A Simple Forwarder Bot Built with Pyrogram to Forward Messages from One Channel to Another</h4>

<h2 align="center">I will be soon releasing an update on this bot to make forwarding more easy. Stay Tuned and join [CodeXBotz](https://t.me/CodeXBotz) for further updates</h2>


# Easy Way
[![Deploy](https://www.herokucdn.com/deploy/button.svg)](https://heroku.com/deploy)

# Normal Way
```python3
git clone https://github.com/rahulps1000/ForwardBot
cd ForwardBot
pip install -r requirements.txt

python3 -m forwardbot
      or 
python -m forwardbot
```

# Docker
# Stop container
docker stop forwardbot

# Start container
docker start forwardbot

# Restart container
docker restart forwardbot

# View logs
docker logs -f forwardbot

# Rebuild and restart
docker stop forwardbot
docker rm forwardbot
docker build -t forward .
docker run -d --restart=unless-stopped --name forwardbot forward

## Main Commands
**Command :** ```/forward``` <br />
**Usage :** Forwards messages from one channel to another (standard method). Fast but won't work with protected channels. <br />

**Command :** ```/copy``` <br />
**Usage :** Copy messages from protected/restricted channels using download-upload method. Works with channels where forwarding is disabled. Slower but bypasses restrictions. <br />

**Command :** ```/status``` <br />
**Usage :** Check the current forwarding/copying status. <br />

**Command :** ```/cancel``` <br />
**Usage :** Cancel the current operation and restart bot. <br />

**Command :** ```/help``` <br />
**Usage :** Get detailed help about using the bot. <br />

## Features
- ✅ **Standard Forwarding** - Fast forwarding for normal channels
- ✅ **Protected Channel Support** - Copy from restricted/protected channels
- ✅ **Download-Upload Method** - Bypass forward restrictions
- ✅ **Public & Private Channels** - Works with both types (must be joined)
- ✅ **Media Type Filtering** - Forward/copy specific types (Photos, Videos, Documents, All)
- ✅ **Flood Protection** - Automatic delays to avoid bans
- ✅ **Real-time Status** - Live updates on progress

## When to Use Each Command

### Use `/forward` when:
- Channel allows forwarding
- You want faster processing
- Source channel is not protected

### Use `/copy` when:
- Channel has forward restrictions
- Channel is protected/restricted
- You want to bypass forward detection
- You need to re-upload content without forward tag

<br />

# Credits
Special thanks to [Subinps](https://github.com/subinps) for Contributing to create this bot

# Thanks
Thanks to [Sandy](https://github.com/sandy1709) for sharing the media_type function from [CatUserBot](https://github.com/sandy1709/catuserbot).

# Licence
[![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl-3.0.en.html)  

ForwardBot is Free Software: You can use, study share and improve it at your
will. Specifically you can redistribute and/or modify it under the terms of the
[GNU General Public License](https://www.gnu.org/licenses/gpl.html) as
published by the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
