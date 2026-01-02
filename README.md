# ForwardBot

<p align="center"><a href="#"><img src="https://telegra.ph/file/fa4d9d23a211f6bcf807b.jpg" width="250"></a></p>
<h1 align="center"><b>Forwarder Bot</b></h1>
<h4 align="center">A Powerful Telegram Bot Built with Pyrogram to Forward and Copy Messages Between Channels</h4>

<p align="center">
  <a href="https://github.com/rahulps1000/ForwardBot"><img src="https://img.shields.io/github/stars/rahulps1000/ForwardBot?style=flat-square" alt="GitHub stars"></a>
  <a href="https://github.com/rahulps1000/ForwardBot/blob/main/LICENSE"><img src="https://img.shields.io/github/license/rahulps1000/ForwardBot?style=flat-square" alt="License"></a>
  <a href="https://github.com/rahulps1000/ForwardBot/issues"><img src="https://img.shields.io/github/issues/rahulps1000/ForwardBot?style=flat-square" alt="Issues"></a>
  <a href="https://github.com/rahulps1000/ForwardBot/pulls"><img src="https://img.shields.io/github/issues-pr/rahulps1000/ForwardBot?style=flat-square" alt="Pull Requests"></a>
</p>

## 📋 Table of Contents

- [Features](#features)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
  - [Easy Deploy (Heroku)](#easy-deploy-heroku)
  - [Manual Installation](#manual-installation)
  - [Docker](#docker)
- [Configuration](#configuration)
- [Usage](#usage)
- [Commands](#commands)
- [Contributing](#contributing)
- [Credits](#credits)
- [License](#license)

## ✨ Features

- 🚀 **Standard Forwarding** - Fast forwarding for normal channels
- 🔒 **Protected Channel Support** - Copy from restricted/protected channels
- 📥 **Download-Upload Method** - Bypass forward restrictions
- 🌐 **Public & Private Channels** - Works with both types (must be joined)
- 🎯 **Media Type Filtering** - Forward/copy specific types (Photos, Videos, Documents, All)
- 🛡️ **Flood Protection** - Automatic delays to avoid bans
- 📊 **Real-time Status** - Live updates on progress
- ⚡ **Asynchronous Processing** - Efficient handling of large operations
- 🔧 **Customizable Commands** - Configurable command handlers

## 📋 Prerequisites

- Python 3.7 or higher
- Telegram API credentials (API_ID and API_HASH)
- Bot Token from [@BotFather](https://t.me/BotFather)
- Pyrogram session string for user account

## 🚀 Installation

### Manual Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/rahulps1000/ForwardBot.git
   cd ForwardBot
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables** (see [Configuration](#configuration))

4. **Run the bot:**
   ```bash
   python3 -m forwardbot
   # or
   python -m forwardbot
   ```

### Docker

#### Build and Run
```bash
# Build the image
docker build -t forwardbot .

# Run the container
docker run -d --restart=unless-stopped --name forwardbot forwardbot
```

#### Docker Commands
```bash
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
docker build -t forwardbot .
docker run -d --restart=unless-stopped --name forwardbot forwardbot
```

## ⚙️ Configuration

Create a `.env` file or set environment variables:

```env
API_ID=your_api_id
API_HASH=your_api_hash
BOT_TOKEN=your_bot_token
STRING_SESSION=your_pyrogram_session_string
SUDO_USERS=user_id1 user_id2
COMMAND_HAND_LER=/
```

### Getting API Credentials

1. Go to [my.telegram.org](https://my.telegram.org) and log in
2. Create an app to get API_ID and API_HASH

### Creating Bot Token

1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Use `/newbot` command and follow instructions

### Generating Session String

Use the included session generator or follow Pyrogram documentation.

## 📖 Usage

1. Start the bot with your configured token
2. Add the bot as admin to source and destination channels
3. Use commands to forward or copy messages

## 🤖 Commands

| Command | Description |
|---------|-------------|
| `/forward` | Forward messages from one channel to another (standard method). Fast but won't work with protected channels. |
| `/copy` | Copy messages from protected/restricted channels using download-upload method. Works with channels where forwarding is disabled. Slower but bypasses restrictions. |
| `/status` | Check the current forwarding/copying status. |
| `/cancel` | Cancel the current operation and restart bot. |
| `/help` | Get detailed help about using the bot. |

### When to Use Each Command

#### Use `/forward` when:
- Channel allows forwarding
- You want faster processing
- Source channel is not protected

#### Use `/copy` when:
- Channel has forward restrictions
- Channel is protected/restricted
- You want to bypass forward detection
- You need to re-upload content without forward tag

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 🙏 Credits

- **Subinps** - For contributing to create this bot
- **Sandy** - For sharing the media_type function from [CatUserBot](https://github.com/sandy1709/catuserbot)

## 📄 License

[![GNU GPLv3 Image](https://www.gnu.org/graphics/gplv3-127x51.png)](http://www.gnu.org/licenses/gpl-3.0.en.html)

ForwardBot is Free Software: You can use, study share and improve it at your will. Specifically you can redistribute and/or modify it under the terms of the [GNU General Public License](https://www.gnu.org/licenses/gpl.html) as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.
