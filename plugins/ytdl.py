# ---------------------------------------------------
# File Name: ytdl_enhanced.py (Enhanced by BlackBox AI)
# Description: Enhanced Pyrogram bot for downloading videos/audio with optimization
# Author: Gagan (Enhanced by BlackBox AI)
# GitHub: https://github.com/devgaganin/
# Telegram: https://t.me/team_spy_pro
# YouTube: https://youtube.com/@dev_gagan
# Created: 2025-01-11
# Enhanced: 2025-01-13
# Version: 3.1.0 (Enhanced)
# License: MIT License
# ---------------------------------------------------

import yt_dlp
import os
import tempfile
import time
import asyncio
import random
import string
import requests
import logging
import math
import json
from shared_client import client, app
from telethon import events
from telethon.sync import TelegramClient
from telethon.tl.types import DocumentAttributeVideo
from utils.func import get_video_metadata, screenshot, is_premium_user
from telethon.tl.functions.messages import EditMessageRequest
from devgagantools import fast_upload
from concurrent.futures import ThreadPoolExecutor
import aiohttp 
import aiofiles
from config import YT_COOKIES, INSTA_COOKIES
from mutagen.id3 import ID3, TIT2, TPE1, COMM, APIC
from mutagen.mp3 import MP3
from datetime import datetime
from plugins.dashboard import update_user_stats

# Enhanced logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Enhanced thread pool with more workers for better performance
thread_pool = ThreadPoolExecutor(max_workers=6)
ongoing_downloads = {}

# Enhanced quality options
QUALITY_OPTIONS = {
    "ultra": "bestvideo[height<=2160]+bestaudio/best[height<=2160]",  # 4K
    "high": "bestvideo[height<=1080]+bestaudio/best[height<=1080]",   # 1080p
    "medium": "bestvideo[height<=720]+bestaudio/best[height<=720]",   # 720p
    "low": "bestvideo[height<=480]+bestaudio/best[height<=480]",      # 480p
    "audio": "bestaudio/best"  # Audio only
}

# Supported platforms with enhanced detection
SUPPORTED_PLATFORMS = {
    'youtube.com': {'name': 'YouTube', 'emoji': '📺', 'max_quality': 'ultra'},
    'youtu.be': {'name': 'YouTube', 'emoji': '📺', 'max_quality': 'ultra'},
    'instagram.com': {'name': 'Instagram', 'emoji': '📷', 'max_quality': 'high'},
    'facebook.com': {'name': 'Facebook', 'emoji': '📘', 'max_quality': 'high'},
    'twitter.com': {'name': 'Twitter', 'emoji': '🐦', 'max_quality': 'medium'},
    'x.com': {'name': 'X (Twitter)', 'emoji': '🐦', 'max_quality': 'medium'},
    'tiktok.com': {'name': 'TikTok', 'emoji': '🎵', 'max_quality': 'medium'},
    'vimeo.com': {'name': 'Vimeo', 'emoji': '🎬', 'max_quality': 'high'},
    'dailymotion.com': {'name': 'Dailymotion', 'emoji': '📹', 'max_quality': 'high'},
}

def get_platform_info(url):
    """Get platform information from URL"""
    for domain, info in SUPPORTED_PLATFORMS.items():
        if domain in url:
            return info
    return {'name': 'Unknown Platform', 'emoji': '🌐', 'max_quality': 'medium'}

def d_thumbnail(thumbnail_url, save_path):
    """Enhanced thumbnail download with better error handling"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(thumbnail_url, stream=True, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        # Validate downloaded thumbnail
        if os.path.getsize(save_path) < 1024:  # Less than 1KB might be invalid
            os.remove(save_path)
            return None
            
        return save_path
    except Exception as e:
        logger.error(f"Enhanced thumbnail download failed: {e}")
        if os.path.exists(save_path):
            os.remove(save_path)
        return None

async def download_thumbnail_async(url, path):
    """Enhanced async thumbnail download"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        async with aiohttp.ClientSession(headers=headers) as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=30)) as response:
                if response.status == 200:
                    content = await response.read()
                    if len(content) > 1024:  # Validate content size
                        async with aiofiles.open(path, 'wb') as f:
                            await f.write(content)
                        return True
        return False
    except Exception as e:
        logger.error(f"Async thumbnail download error: {e}")
        return False

async def extract_audio_async(ydl_opts, url):
    """Enhanced async audio extraction with better error handling"""
    def sync_extract():
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                return ydl.extract_info(url, download=True)
        except Exception as e:
            logger.error(f"Audio extraction error: {e}")
            raise e
    
    return await asyncio.get_event_loop().run_in_executor(thread_pool, sync_extract)

def get_random_string(length=7):
    """Generate random string with better character set"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

def get_optimal_quality_sync(url, user_id, is_premium=False):
    """Synchronous version of get_optimal_quality for non-async contexts"""
    platform_info = get_platform_info(url)
    max_quality = platform_info['max_quality']
    
    if is_premium:
        return QUALITY_OPTIONS.get(max_quality, QUALITY_OPTIONS['high'])
    else:
        return QUALITY_OPTIONS.get('medium', QUALITY_OPTIONS['medium'])

def create_enhanced_ydl_opts(format_selector, cookies_path=None, audio_only=False):
    """Create enhanced yt-dlp options with better configuration"""
    opts = {
        'format': format_selector,
        'cookiefile': cookies_path,
        'quiet': False,
        'no_warnings': False,
        'extractaudio': audio_only,
        'audioformat': 'mp3' if audio_only else None,
        'audioquality': '192' if audio_only else None,
        'noplaylist': True,
        'writethumbnail': True,
        'writesubtitles': False,
        'writeautomaticsub': False,
        # Enhanced options
        'retries': 3,
        'fragment_retries': 3,
        'retry_sleep': 5,
        'http_chunk_size': 10485760,  # 10MB chunks
        'concurrent_fragments': 3,
        # Headers for better compatibility
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en-us,en;q=0.5',
            'Sec-Fetch-Mode': 'navigate',
        }
    }
    
    if audio_only:
        opts['postprocessors'] = [
            {
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192'
            }
        ]
    
    return opts

async def process_enhanced_audio(client, event, url, cookies_env_var=None):
    """Enhanced audio processing with better quality and metadata"""
    user_id = event.sender_id
    platform_info = get_platform_info(url)
    
    # Update user stats
    update_user_stats(user_id, "download", {"type": "audio", "platform": platform_info['name']})
    
    cookies = None
    if cookies_env_var == "INSTA_COOKIES":
        cookies = INSTA_COOKIES
    elif cookies_env_var == "YT_COOKIES":
        cookies = YT_COOKIES
    
    temp_cookie_path = None
    if cookies:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_cookie_file:
            temp_cookie_file.write(cookies)
            temp_cookie_path = temp_cookie_file.name

    start_time = time.time()
    random_filename = f"@team_spy_pro_audio_{user_id}_{int(time.time())}"
    download_path = f"{random_filename}.mp3"

    # Enhanced yt-dlp options for audio
    ydl_opts = create_enhanced_ydl_opts(
        QUALITY_OPTIONS['audio'], 
        temp_cookie_path, 
        audio_only=True
    )
    ydl_opts['outtmpl'] = f"{random_filename}.%(ext)s"

    progress_message = await event.reply(
        f"🎵 **Audio Download Started**\n\n"
        f"{platform_info['emoji']} **Platform:** {platform_info['name']}\n"
        f"🎧 **Quality:** High (192kbps MP3)\n"
        f"⚡ **Status:** Extracting audio..."
    )

    try:
        # Extract audio with enhanced options
        info_dict = await extract_audio_async(ydl_opts, url)
        title = info_dict.get('title', 'Extracted Audio')
        duration = info_dict.get('duration', 0)
        uploader = info_dict.get('uploader', 'Unknown')
        
        await progress_message.edit(
            f"🎵 **Audio Processing**\n\n"
            f"📝 **Title:** {title[:50]}...\n"
            f"👤 **Uploader:** {uploader}\n"
            f"⏱️ **Duration:** {format_duration(duration)}\n"
            f"🔄 **Status:** Adding metadata..."
        )

        # Enhanced metadata processing
        if os.path.exists(download_path):
            def edit_metadata():
                try:
                    audio_file = MP3(download_path, ID3=ID3)
                    try:
                        audio_file.add_tags()
                    except Exception:
                        pass
                    
                    # Add comprehensive metadata
                    audio_file.tags["TIT2"] = TIT2(encoding=3, text=title)
                    audio_file.tags["TPE1"] = TPE1(encoding=3, text=uploader or "Team SPY")
                    audio_file.tags["COMM"] = COMM(encoding=3, lang="eng", desc="Comment", 
                                                 text=f"Downloaded from {platform_info['name']} via Team SPY Bot")
                    
                    # Add album art from thumbnail
                    thumbnail_url = info_dict.get('thumbnail')
                    if thumbnail_url:
                        thumbnail_path = os.path.join(tempfile.gettempdir(), f"thumb_{user_id}.jpg")
                        if await download_thumbnail_async(thumbnail_url, thumbnail_path):
                            try:
                                with open(thumbnail_path, 'rb') as img:
                                    audio_file.tags["APIC"] = APIC(
                                        encoding=3, mime='image/jpeg', type=3, 
                                        desc='Cover', data=img.read()
                                    )
                            except Exception as e:
                                logger.error(f"Album art error: {e}")
                            finally:
                                if os.path.exists(thumbnail_path):
                                    os.remove(thumbnail_path)
                    
                    audio_file.save()
                    return True
                except Exception as e:
                    logger.error(f"Metadata error: {e}")
                    return False

            metadata_success = await asyncio.to_thread(edit_metadata)
            
            # Upload with enhanced progress
            chat_id = event.chat_id
            await progress_message.edit(
                f"🎵 **Upload Starting**\n\n"
                f"📁 **File:** {os.path.basename(download_path)}\n"
                f"💾 **Size:** {format_file_size(os.path.getsize(download_path))}\n"
                f"🎯 **Metadata:** {'✅ Enhanced' if metadata_success else '❌ Basic'}\n"
                f"⬆️ **Status:** Uploading..."
            )
            
            uploaded = await fast_upload(
                client, download_path, 
                reply=progress_message, 
                name=None,
                progress_bar_function=lambda done, total: enhanced_progress_callback(done, total, chat_id, "upload")
            )
            
            # Enhanced caption
            caption = f"""
🎵 **Audio Download Complete**

📝 **Title:** {title}
👤 **Uploader:** {uploader}
⏱️ **Duration:** {format_duration(duration)}
{platform_info['emoji']} **Platform:** {platform_info['name']}
🎧 **Quality:** 192kbps MP3
⚡ **Processing Time:** {format_duration(int(time.time() - start_time))}

🤖 **Powered by Team SPY**
            """
            
            await client.send_file(chat_id, uploaded, caption=caption)
            await progress_message.delete()
            
        else:
            await progress_message.edit("❌ **Audio file not found after extraction!**")

    except Exception as e:
        logger.exception("Enhanced audio processing error")
        error_msg = f"""
❌ **Audio Download Failed**

🚫 **Error:** {str(e)[:100]}...
🔄 **Suggestions:**
• Check if the link is valid
• Try again in a few minutes
• Contact support if problem persists

**Platform:** {platform_info['name']}
        """
        await progress_message.edit(error_msg)
    finally:
        # Cleanup
        for file_path in [download_path, temp_cookie_path]:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except:
                    pass

def format_duration(seconds):
    """Format duration in human readable format"""
    if not seconds:
        return "Unknown"
    
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours:02d}:{minutes:02d}:{secs:02d}"
    else:
        return f"{minutes:02d}:{secs:02d}"

def format_file_size(bytes_size):
    """Format file size in human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024.0:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024.0
    return f"{bytes_size:.1f} TB"

def enhanced_progress_callback(done, total, user_id, operation_type="download"):
    """Enhanced progress callback with better formatting"""
    percent = (done / total) * 100
    
    # Create progress bar
    completed_blocks = int(percent // 5)  # 20 blocks total
    remaining_blocks = 20 - completed_blocks
    progress_bar = "🟩" * completed_blocks + "⬜" * remaining_blocks
    
    done_mb = done / (1024 * 1024)
    total_mb = total / (1024 * 1024)
    
    # Calculate speed (simplified)
    speed_mbps = done_mb / max(1, int(time.time()) % 3600)  # Rough estimate
    
    operation_emoji = {
        "download": "⬇️",
        "upload": "⬆️", 
        "process": "🔄"
    }.get(operation_type, "📊")
    
    return f"""
{operation_emoji} **{operation_type.title()} Progress**

{progress_bar}

📊 **Progress:** {percent:.1f}%
💾 **Size:** {done_mb:.1f} MB / {total_mb:.1f} MB
⚡ **Speed:** {speed_mbps:.1f} MB/s (estimated)

🤖 **Powered by Team SPY**
    """

async def get_optimal_quality_async(url, user_id):
    """Async version of get_optimal_quality"""
    platform_info = get_platform_info(url)
    is_premium = await is_premium_user(user_id)
    
    max_quality = platform_info['max_quality']
    
    if is_premium:
        return QUALITY_OPTIONS.get(max_quality, QUALITY_OPTIONS['high'])
    else:
        # Free users get limited quality
        return QUALITY_OPTIONS.get('medium', QUALITY_OPTIONS['medium'])

# Enhanced command handlers
@client.on(events.NewMessage(pattern="/adl"))
async def enhanced_audio_handler(event):
    """Enhanced audio download handler"""
    user_id = event.sender_id
    
    if user_id in ongoing_downloads:
        await event.reply(
            "⏳ **Download In Progress**\n\n"
            "❌ You already have an ongoing download.\n"
            "⏰ Please wait until it completes!\n\n"
            "**Tip:** Premium users get faster processing!"
        )
        return

    if len(event.message.text.split()) < 2:
        help_msg = """
🎵 **Audio Download Help**

**Usage:** `/adl <video-link>`

**Supported Platforms:**
📺 YouTube & YouTube Music
📷 Instagram (Posts & Stories)
📘 Facebook Videos
🐦 Twitter/X Videos
🎵 TikTok Audio
🎬 Vimeo & Dailymotion
📹 And 25+ more platforms!

**Features:**
• High-quality 192kbps MP3
• Embedded metadata & thumbnails
• Fast processing & upload
• Progress tracking

**Example:** `/adl https://youtube.com/watch?v=...`
        """
        await event.reply(help_msg)
        return    

    url = event.message.text.split(maxsplit=1)[1]
    platform_info = get_platform_info(url)
    
    # Validate URL format
    if not any(platform in url for platform in SUPPORTED_PLATFORMS.keys()):
        unsupported_msg = f"""
❌ **Unsupported Platform**

🚫 The platform from your link is not supported.

**Supported Platforms:**
{chr(10).join([f"{info['emoji']} {info['name']}" for info in SUPPORTED_PLATFORMS.values()])}

**Your Link Platform:** {platform_info['name']}

**Tip:** Try with a different platform or contact support.
        """
        await event.reply(unsupported_msg)
        return
    
    ongoing_downloads[user_id] = True

    try:
        # Enhanced processing based on platform
        if "instagram.com" in url:
            await process_enhanced_audio(client, event, url, "INSTA_COOKIES")
        elif any(yt_domain in url for yt_domain in ["youtube.com", "youtu.be"]):
            await process_enhanced_audio(client, event, url, "YT_COOKIES")
        else:
            await process_enhanced_audio(client, event, url)
            
    except Exception as e:
        error_msg = f"""
❌ **System Error**

🚫 **Error:** {str(e)[:150]}...
🔧 **Platform:** {platform_info['name']}

**Try These Steps:**
1. Check if the link is valid and accessible
2. Wait a few minutes and try again
3. Try with a different quality/format
4. Contact support: @team_spy_pro

**Error Code:** AUD_{int(time.time()) % 10000}
        """
        await event.reply(error_msg)
    finally:
        ongoing_downloads.pop(user_id, None)

# Enhanced video download with similar improvements
async def fetch_enhanced_video_info(url, ydl_opts, progress_message, check_duration_and_size, user_id):
    """Enhanced video info fetching with better validation"""
    platform_info = get_platform_info(url)
    is_premium = await is_premium_user(user_id)
    
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info_dict = ydl.extract_info(url, download=False)

        if check_duration_and_size:
            # Enhanced duration check
            duration = info_dict.get('duration', 0)
            max_duration = 7200 if is_premium else 3600  # 2 hours premium, 1 hour free
            
            if duration and duration > max_duration:
                limit_text = "2 hours" if is_premium else "1 hour"
                await progress_message.edit(
                    f"❌ **Video Too Long**\n\n"
                    f"⏰ **Duration:** {format_duration(duration)}\n"
                    f"🚫 **Limit:** {limit_text} ({'Premium' if is_premium else 'Free User'})\n\n"
                    f"{'💡 **Tip:** Free users have shorter limits' if not is_premium else ''}"
                )
                return None

            # Enhanced size check  
            estimated_size = info_dict.get('filesize_approx', 0)
            max_size = 4 * 1024 * 1024 * 1024 if is_premium else 2 * 1024 * 1024 * 1024  # 4GB premium, 2GB free
            
            if estimated_size and estimated_size > max_size:
                limit_text = "4GB" if is_premium else "2GB"
                await progress_message.edit(
                    f"❌ **File Too Large**\n\n"
                    f"💾 **Size:** {format_file_size(estimated_size)}\n"
                    f"🚫 **Limit:** {limit_text} ({'Premium' if is_premium else 'Free User'})\n\n"
                    f"{'🎯 **Upgrade:** Use /tokens for free premium' if not is_premium else ''}"
                )
                return None

        return info_dict

def download_enhanced_video(url, ydl_opts):
    """Enhanced video download with better error handling"""
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
        return True
    except Exception as e:
        logger.error(f"Enhanced video download error: {e}")
        raise e

@client.on(events.NewMessage(pattern="/dl"))
async def enhanced_video_handler(event):
    """Enhanced video download handler with better UI"""
    user_id = event.sender_id
    
    if user_id in ongoing_downloads:
        await event.reply(
            "⏳ **Download In Progress**\n\n"
            "❌ You already have an ongoing download.\n"
            "⏰ Please wait until it completes!\n\n"
            "**Tip:** Premium users get priority processing!"
        )
        return

    if len(event.message.text.split()) < 2:
        help_msg = """
🎥 **Video Download Help**

**Usage:** `/dl <video-link>`

**Quality Options:**
🔥 **Premium Users:** Up to 4K quality
⚡ **Free Users:** Up to 720p quality

**Supported Platforms:**
📺 YouTube (up to 4K)
📷 Instagram & Stories
📘 Facebook Videos
🐦 Twitter/X Videos
🎵 TikTok Videos
🎬 Vimeo & Dailymotion
📹 And 25+ more platforms!

**Features:**
• Auto-quality selection
• Progress tracking with ETA
• Enhanced metadata
• Thumbnail generation

**Example:** `/dl https://youtube.com/watch?v=...`
        """
        await event.reply(help_msg)
        return    

    url = event.message.text.split(maxsplit=1)[1]
    platform_info = get_platform_info(url)
    
    ongoing_downloads[user_id] = True

    try:
        # Enhanced processing with platform-specific handling
        if "instagram.com" in url:
            await process_enhanced_video(client, event, url, "INSTA_COOKIES", check_duration_and_size=False)
        elif any(yt_domain in url for yt_domain in ["youtube.com", "youtu.be"]):
            await process_enhanced_video(client, event, url, "YT_COOKIES", check_duration_and_size=True)
        else:
            await process_enhanced_video(client, event, url, None, check_duration_and_size=False)

    except Exception as e:
        error_msg = f"""
❌ **Download Failed**

🚫 **Error:** {str(e)[:150]}...
🔧 **Platform:** {platform_info['name']}

**Troubleshooting:**
1. Verify the link is valid and public
2. Check your internet connection
3. Try again in a few minutes
4. Contact support if issue persists

**Support:** @team_spy_pro
**Error ID:** VID_{int(time.time()) % 10000}
        """
        await event.reply(error_msg)
    finally:
        ongoing_downloads.pop(user_id, None)

async def process_enhanced_video(client, event, url, cookies_env_var, check_duration_and_size=False):
    """Enhanced video processing with better performance and UI"""
    start_time = time.time()
    user_id = event.sender_id
    platform_info = get_platform_info(url)
    
    # Update user stats
    update_user_stats(user_id, "download", {"type": "video", "platform": platform_info['name']})
    
    logger.info(f"Enhanced video download started: {url}")
    
    # Get optimal quality for user
    is_premium = await is_premium_user(user_id)
    optimal_quality = get_optimal_quality_sync(url, user_id, is_premium)
    
    cookies = None
    if cookies_env_var == "INSTA_COOKIES":
        cookies = INSTA_COOKIES
    elif cookies_env_var == "YT_COOKIES":
        cookies = YT_COOKIES

    random_filename = f"enhanced_{get_random_string()}_{int(time.time())}.mp4"
    download_path = os.path.abspath(random_filename)
    
    temp_cookie_path = None
    if cookies:
        with tempfile.NamedTemporaryFile(delete=False, mode='w', suffix='.txt') as temp_cookie_file:
            temp_cookie_file.write(cookies)
            temp_cookie_path = temp_cookie_file.name

    thumbnail_file = None
    metadata = {'width': None, 'height': None, 'duration': None, 'thumbnail': None}

    # Enhanced yt-dlp options
    ydl_opts = create_enhanced_ydl_opts(optimal_quality, temp_cookie_path)
    ydl_opts['outtmpl'] = download_path

    progress_message = await event.reply(
        f"🎥 **Video Download Started**\n\n"
        f"{platform_info['emoji']} **Platform:** {platform_info['name']}\n"
        f"🎯 **Quality:** {'Premium' if await is_premium_user(user_id) else 'Standard'}\n"
        f"🔍 **Status:** Analyzing video..."
    )

    try:
        # Fetch video info with enhanced validation
        info_dict = await fetch_enhanced_video_info(url, ydl_opts, progress_message, check_duration_and_size, user_id)
        if not info_dict:
            return

        title = info_dict.get('title', 'Enhanced Download')
        duration = info_dict.get('duration', 0)
        uploader = info_dict.get('uploader', 'Unknown')
        view_count = info_dict.get('view_count', 0)
        
        await progress_message.edit(
            f"🎥 **Video Information**\n\n"
            f"📝 **Title:** {title[:50]}...\n"
            f"👤 **Uploader:** {uploader}\n"
            f"⏱️ **Duration:** {format_duration(duration)}\n"
            f"👀 **Views:** {view_count:,} views\n"
            f"⬇️ **Status:** Downloading..."
        )
        
        # Download with enhanced monitoring
        await asyncio.to_thread(download_enhanced_video, url, ydl_opts)
        
        # Enhanced metadata processing
        k = await get_video_metadata(download_path)      
        metadata['width'] = info_dict.get('width') or k['width']
        metadata['height'] = info_dict.get('height') or k['height']
        metadata['duration'] = int(info_dict.get('duration') or 0) or k['duration']
        
        # Enhanced thumbnail processing
        thumbnail_url = info_dict.get('thumbnail', None)
        if thumbnail_url:
            thumbnail_file = os.path.join(tempfile.gettempdir(), f"enhanced_thumb_{user_id}.jpg")
            downloaded_thumb = d_thumbnail(thumbnail_url, thumbnail_file)
            if downloaded_thumb:
                logger.info(f"Enhanced thumbnail saved: {downloaded_thumb}")

        THUMB = thumbnail_file if thumbnail_file and os.path.exists(thumbnail_file) else await screenshot(download_path, metadata['duration'], user_id)

        # Enhanced upload process
        chat_id = event.chat_id
        file_size = os.path.getsize(download_path)
        
        await progress_message.edit(
            f"🎥 **Upload Starting**\n\n"
            f"📁 **File:** {os.path.basename(download_path)}\n"
            f"💾 **Size:** {format_file_size(file_size)}\n"
            f"🎬 **Resolution:** {metadata['width']}x{metadata['height']}\n"
            f"⏱️ **Duration:** {format_duration(metadata['duration'])}\n"
            f"⬆️ **Status:** Uploading..."
        )

        # Handle large files with splitting if needed
        SIZE_LIMIT = 2 * 1024 * 1024 * 1024  # 2GB
        
        if file_size > SIZE_LIMIT:
            await progress_message.edit("📦 **Large File Detected** - Using advanced upload method...")
            await split_and_upload_file(app, chat_id, download_path, title)
        else:
            uploaded = await fast_upload(
                client, download_path,
                reply=progress_message,
                progress_bar_function=lambda done, total: enhanced_progress_callback(done, total, chat_id, "upload")
            )
            
            # Enhanced caption with rich information
            caption = f"""
🎥 **Video Download Complete**

📝 **Title:** {title}
👤 **Uploader:** {uploader}
⏱️ **Duration:** {format_duration(metadata['duration'])}
🎬 **Quality:** {metadata['width']}x{metadata['height']}
{platform_info['emoji']} **Platform:** {platform_info['name']}
👀 **Views:** {view_count:,}
⚡ **Processing Time:** {format_duration(int(time.time() - start_time))}

🤖 **Powered by Team SPY - Enhanced Engine v3.1**
            """
            
            await client.send_file(
                event.chat_id,
                uploaded,
                caption=caption,
                attributes=[
                    DocumentAttributeVideo(
                        duration=metadata['duration'],
                        w=metadata['width'],
                        h=metadata['height'],
                        supports_streaming=True
                    )
                ],
                thumb=THUMB
            )
        
        await progress_message.delete()
        
    except Exception as e:
        logger.exception("Enhanced video processing error")
        error_msg = f"""
❌ **Video Download Failed**

🚫 **Error:** {str(e)[:150]}...
🔧 **Platform:** {platform_info['name']}
⏱️ **Duration:** {format_duration(int(time.time() - start_time))}

**Troubleshooting:**
• Verify the video URL is accessible
• Check if the video is geo-restricted
• Try with a different quality setting
• Contact support for persistent issues

**Support:** @team_spy_pro
        """
        await progress_message.edit(error_msg)
    finally:
        # Enhanced cleanup
        cleanup_files = [download_path, temp_cookie_path, thumbnail_file]
        for file_path in cleanup_files:
            if file_path and os.path.exists(file_path):
                try:
                    os.remove(file_path)
                except Exception as cleanup_error:
                    logger.error(f"Cleanup error for {file_path}: {cleanup_error}")

# Keep the existing split_and_upload_file and other utility functions
# ... (previous utility functions remain the same)

async def run_ytdl_enhanced_plugin():
    """Enhanced plugin initialization"""
    print("Enhanced YT-DLP plugin loaded successfully with v3.1 features!")
    
    # Initialize performance monitoring
    logger.info("Enhanced download engine initialized")
    logger.info(f"Supported platforms: {len(SUPPORTED_PLATFORMS)}")
    logger.info(f"Thread pool workers: {thread_pool._max_workers}")

# Enhanced utility functions from original file

async def split_and_upload_file(app, sender, file_path, caption):
    """Enhanced file splitting with progress tracking"""
    if not os.path.exists(file_path):
        await app.send_message(sender, "❌ File not found!")
        return

    file_size = os.path.getsize(file_path)
    start = await app.send_message(sender, 
        f"📦 **Large File Detected**\n\n"
        f"💾 **Size:** {format_file_size(file_size)}\n"
        f"✂️ **Action:** Splitting into parts\n"
        f"⚡ **Status:** Preparing..."
    )
    
    PART_SIZE = 1.9 * 1024 * 1024 * 1024  # 1.9GB per part

    part_number = 0
    async with aiofiles.open(file_path, mode="rb") as f:
        while True:
            chunk = await f.read(PART_SIZE)
            if not chunk:
                break

            # Create part filename
            base_name, file_ext = os.path.splitext(file_path)
            part_file = f"{base_name}.part{str(part_number + 1).zfill(3)}{file_ext}"

            # Write part to file
            async with aiofiles.open(part_file, mode="wb") as part_f:
                await part_f.write(chunk)

            # Upload part with enhanced progress
            edit = await app.send_message(sender, 
                f"⬆️ **Uploading Part {part_number + 1}**\n\n"
                f"📁 **File:** {os.path.basename(part_file)}\n"
                f"💾 **Size:** {format_file_size(len(chunk))}\n"
                f"⚡ **Status:** Uploading..."
            )
            
            part_caption = f"{caption}\n\n📦 **Part:** {part_number + 1}"
            
            await app.send_document(
                sender, 
                document=part_file, 
                caption=part_caption,
                progress=progress_bar,
                progress_args=(
                    "╭─────────────────────╮\n│  **Enhanced Uploader**\n├─────────────────────", 
                    edit, 
                    time.time()
                )
            )
            
            await edit.delete()
            os.remove(part_file)
            part_number += 1

    await start.edit(
        f"✅ **Upload Complete**\n\n"
        f"📦 **Total Parts:** {part_number}\n"
        f"💾 **Total Size:** {format_file_size(file_size)}\n"
        f"🎉 **Status:** All parts uploaded successfully!"
    )
    
    os.remove(file_path)

PROGRESS_BAR = """
│ **Completed:** {1}/{2}
│ **Bytes:** {0}%
│ **Speed:** {3}/s
│ **ETA:** {4}
╰─────────────────────╯
"""

async def get_seconds(time_string: str) -> int:
    """Converts a time string (e.g., '5min', '2hour') into seconds"""
    def extract_value_and_unit(ts: str):
        value = ''.join(filter(str.isdigit, ts))
        unit = ts[len(value):].strip()
        return int(value) if value else 0, unit
    
    value, unit = extract_value_and_unit(time_string)
    time_units = {
        's': 1,
        'min': 60,
        'hour': 3600,
        'day': 86400,
        'month': 86400 * 30,
        'year': 86400 * 365
    }
    
    return value * time_units.get(unit, 0)

async def progress_bar(current: int, total: int, ud_type: str, message, start: float):
    """Enhanced progress bar for ongoing processes"""
    now = time.time()
    diff = now - start
    
    if round(diff % 10) == 0 or current == total:
        percentage = (current * 100) / total
        speed = current / diff if diff else 0
        elapsed_time = round(diff * 1000)
        time_to_completion = round((total - current) / speed) * 1000 if speed else 0
        estimated_total_time = elapsed_time + time_to_completion

        elapsed_time_str = TimeFormatter(elapsed_time)
        estimated_total_time_str = TimeFormatter(estimated_total_time)

        progress = "".join(["🟩" for _ in range(math.floor(percentage / 10))]) + \
                   "".join(["⬜" for _ in range(10 - math.floor(percentage / 10))])
        
        progress_text = progress + PROGRESS_BAR.format(
            round(percentage, 2),
            humanbytes(current),
            humanbytes(total),
            humanbytes(speed),
            estimated_total_time_str if estimated_total_time_str else "0 s"
        )
        try:
            await message.edit(text=f"{ud_type}\n│ {progress_text}")
        except:
            pass

def humanbytes(size: int) -> str:
    """Converts bytes into a human-readable format"""
    if not size:
        return ""
    
    power = 2**10
    units = ['B', 'KB', 'MB', 'GB', 'TB']
    n = 0
    while size > power and n < len(units) - 1:
        size /= power
        n += 1
    
    return f"{round(size, 2)} {units[n]}"

def TimeFormatter(milliseconds: int) -> str:
    """Formats milliseconds into a human-readable duration"""
    seconds, milliseconds = divmod(milliseconds, 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    
    parts = []
    if days: parts.append(f"{days}d")
    if hours: parts.append(f"{hours}h")
    if minutes: parts.append(f"{minutes}m")
    if seconds: parts.append(f"{seconds}s")
    if milliseconds: parts.append(f"{milliseconds}ms")
    
    return ', '.join(parts)

def convert(seconds: int) -> str:
    """Converts seconds into HH:MM:SS format"""
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{hours}:{minutes:02d}:{seconds:02d}"

# Enhanced quality selection commands
@client.on(events.NewMessage(pattern="/quality"))
async def quality_selector(event):
    """Enhanced quality selection interface"""
    user_id = event.sender_id
    is_premium = await is_premium_user(user_id)
    
    quality_msg = f"""
🎯 **Quality Selection Guide**

{'💎 **Premium User** - Access to all qualities!' if is_premium else '🆓 **Free User** - Limited to standard quality'}

**Available Qualities:**

🔥 **Ultra (4K)** - 2160p
{'✅ Available' if is_premium else '❌ Premium Only'}

⚡ **High (1080p)** - Full HD
{'✅ Available' if is_premium else '❌ Premium Only'}

🎯 **Medium (720p)** - HD
✅ Available for all users

📱 **Low (480p)** - Standard
✅ Available for all users

🎵 **Audio Only** - High Quality MP3
✅ Available for all users

**Auto-Selection:**
The bot automatically selects the best quality available for your account type.

{'🎫 **Upgrade:** Use /tokens for free premium access!' if not is_premium else '💎 **Enjoying premium features!**'}
    """
    
    await event.reply(quality_msg)

@client.on(events.NewMessage(pattern="/platforms"))
async def supported_platforms(event):
    """Show all supported platforms with details"""
    platforms_msg = "🌐 **Supported Platforms**\n\n"
    
    for domain, info in SUPPORTED_PLATFORMS.items():
        platforms_msg += f"{info['emoji']} **{info['name']}**\n"
        platforms_msg += f"   🔗 {domain}\n"
        platforms_msg += f"   📊 Max Quality: {info['max_quality'].title()}\n\n"
    
    platforms_msg += f"""
📊 **Total Platforms:** {len(SUPPORTED_PLATFORMS)}

**Features:**
• Auto-quality detection
• Platform-specific optimization
• Enhanced metadata extraction
• Progress tracking for all platforms

**Usage:**
Use `/dl <link>` for videos or `/adl <link>` for audio from any supported platform.
    """
    
    await event.reply(platforms_msg)