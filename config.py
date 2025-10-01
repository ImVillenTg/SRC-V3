# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# See LICENSE file in the repository root for full license text.

import os
from dotenv import load_dotenv

load_dotenv()

# VPS --- FILL COOKIES 🍪 in """ ... """ 

INST_COOKIES = """
# wtite up here insta cookies
"""

YTUB_COOKIES = """
# Netscape HTTP Cookie File
# Enhanced Indian IP YouTube Cookies
# This is a generated file! Do not edit.

.youtube.com	TRUE	/	FALSE	1767225600	__Secure-1PSIDTS	sidts-CjIB4E2dkQkIJShbq-2x2EMg-HxBdTl9qIJwrZ4o2S5oK8P4l3jP5UfxhX6AQFhbJwcUyRAA
.youtube.com	TRUE	/	FALSE	1767225600	__Secure-3PSIDTS	sidts-CjIB4E2dkQkIJShbq-2x2EMg-HxBdTl9qIJwrZ4o2S5oK8P4l3jP5UfxhX6AQFhbJwcUyRAA
.youtube.com	TRUE	/	FALSE	1767225600	__Secure-1PSIDCC	AKEyXzULzh5E9k5VAEiKXYfLjE4V5HGf9FPX2MlJNUcKyKdlNzMx7aQfEP5WOjd9
.youtube.com	TRUE	/	FALSE	1767225600	__Secure-3PSIDCC	AKEyXzULzh5E9k5VAEiKXYfLjE4V5HGf9FPX2MlJNUcKyKdlNzMx7aQfEP5WOjd9
.youtube.com	TRUE	/	FALSE	1767225600	VISITOR_PRIVACY_METADATA	CgJJTjIKChgIUVCb2OQI2AJB%3D%3D
.youtube.com	TRUE	/	FALSE	1767225600	VISITOR_INFO1_LIVE	R8bYo2_Fxpg
.youtube.com	TRUE	/	TRUE	1798761111	HSID	Af5CYQQkMc1O8gg9K
.youtube.com	TRUE	/	TRUE	1798761111	SSID	AH5CYQQkMc1O8gg9K
.youtube.com	TRUE	/	TRUE	1798761111	APISID	9sF8bEWX9lJ1bVkP/ACb7TcyA5KxOHnF8h
.youtube.com	TRUE	/	TRUE	1798761111	SAPISID	9sF8bEWX9lJ1bVkP/ACb7TcyA5KxOHnF8h
.youtube.com	TRUE	/	TRUE	1798761111	__Secure-1PAPISID	9sF8bEWX9lJ1bVkP/ACb7TcyA5KxOHnF8h
.youtube.com	TRUE	/	TRUE	1798761111	__Secure-3PAPISID	9sF8bEWX9lJ1bVkP/ACb7TcyA5KxOHnF8h
.youtube.com	TRUE	/	FALSE	1767225600	LOGIN_INFO	AFmmF2swRgIhAKtYDgV8t-FxPnEzRkZSrwcD8vUjMhNDHfGzgGnZdNWHAiEA2r2BXJ-VzMQR7K4E8tP3vqJzYIL7r5fL7m1jLXxQk8g:QUQ3MjNmd0t1Y0dVV0M2NnNWU3cxNWg5TUtyMXBMdnFKMllkZW11d1Z5Zm9IRVhwNUJfQkg5TEk2T09wWExxTlFfT2Y5YXhRUm9fMWJnVDFzWU5sVVVBcEdpRGIwWEVOVUxKa2dyUWR3LXJRTHFtMzJjNUhJMzhtMXJpcnFWdmYzVmNmblYzVmd4V3NKYzlWTFBSeFB4aGtjOWhQd3JwZnhkVGk3LUN2ODJlYjhGNg
.youtube.com	TRUE	/	FALSE	1767225600	PREF	f6=40000000&tz=Asia.Kolkata&f5=20000&f7=100&hl=en-IN&gl=IN
.youtube.com	TRUE	/	FALSE	1767225600	YSC	HJW8GfRLHEc
.youtube.com	TRUE	/	FALSE	1735689600	GPS	1
.google.com	TRUE	/	FALSE	1767225600	NID	511=N8YHRl4M9xM-GeoBYpass-Indian-OptimizedCookies-ForVideoDownload
youtube.com	FALSE	/	FALSE	1735689600	CONSENT	YES+cb.20210328-17-p0.en+FX+667
.googlevideo.com	TRUE	/	FALSE	1735689600	__Secure-ENID	17.SE=Geo-Bypass-India-YouTube-Download
"""

API_ID = os.getenv("API_ID", "25576002")
API_HASH = os.getenv("API_HASH", "1238175ae078249640ae6ca93cf1f888")
BOT_TOKEN = os.getenv("BOT_TOKEN", "7503621200:AAEISyANRC6m5BTSSbpgDeUqmquWCqtPLGA")
MONGO_DB = os.getenv("MONGO_DB", "mongodb+srv://techvidder:Yash2Akay@cluster0.hhteeje.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
OWNER_ID = list(map(int, os.getenv("OWNER_ID", "").split())) # list seperated via space
DB_NAME = os.getenv("DB_NAME", "telegram_downloader")
STRING = os.getenv("STRING", None) # optional
LOG_GROUP = int(os.getenv("LOG_GROUP", "-1002020173203")) # optional with -100
FORCE_SUB = int(os.getenv("FORCE_SUB", "-1002406812865")) # optional with -100
MASTER_KEY = os.getenv("MASTER_KEY", "gK8HzLfT9QpViJcYeB5wRa3DmN7P2xUq") # for session encryption
IV_KEY = os.getenv("IV_KEY", "s7Yx5CpVmE3F") # for decryption
YT_COOKIES = os.getenv("YT_COOKIES", YTUB_COOKIES)
INSTA_COOKIES = os.getenv("INSTA_COOKIES", INST_COOKIES)
FREEMIUM_LIMIT = int(os.getenv("FREEMIUM_LIMIT", "3"))
PREMIUM_LIMIT = int(os.getenv("PREMIUM_LIMIT", "500"))
JOIN_LINK = os.getenv("JOIN_LINK", "https://t.me/vidder_tech") # this link for start command message
ADMIN_CONTACT = os.getenv("ADMIN_CONTACT", "https://t.me/vidder_deals")




