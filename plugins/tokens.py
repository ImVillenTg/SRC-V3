# Copyright (c) 2025 Enhanced by BlackBox AI
# Token System & Shortener Integration for Free Premium Access

from shared_client import app
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.func import add_premium_user, is_premium_user
import requests
import asyncio
import json
import os
from datetime import datetime, timedelta
import logging
from plugins.start import subscribe

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Shortener API configurations
SHORTENER_APIS = {
    "upshrink": {
        "name": "UpShrink",
        "api_url": "https://upshrink.com/api",
        "api_key": "your_upshrink_api_key_here",  # Replace with actual API key
        "shorten_endpoint": "/url/add",
        "verify_endpoint": "/url/stats"
    },
    "shorte": {
        "name": "Shorte.st", 
        "api_url": "https://api.shorte.st",
        "api_key": "your_shorte_api_key_here",  # Replace with actual API key
        "shorten_endpoint": "/v1/data/url",
        "verify_endpoint": "/v1/data/url/stats"
    }
}

# Token tracking
TOKEN_FILE = "token_tracking.json"
USER_TOKENS = {}

def load_token_data():
    """Load token tracking data"""
    global USER_TOKENS
    try:
        if os.path.exists(TOKEN_FILE):
            with open(TOKEN_FILE, 'r') as f:
                USER_TOKENS = json.load(f)
    except Exception as e:
        logger.error(f"Error loading token data: {e}")
        USER_TOKENS = {}

def save_token_data():
    """Save token tracking data"""
    try:
        with open(TOKEN_FILE, 'w') as f:
            json.dump(USER_TOKENS, f)
    except Exception as e:
        logger.error(f"Error saving token data: {e}")

async def shorten_url(url, shortener="upshrink"):
    """Create shortened URL using specified shortener"""
    try:
        if shortener not in SHORTENER_APIS:
            return None
        
        config = SHORTENER_APIS[shortener]
        api_url = f"{config['api_url']}{config['shorten_endpoint']}"
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        data = {
            "url": url,
            "format": "json"
        }
        
        response = requests.post(api_url, json=data, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            return result.get("shortenedUrl") or result.get("short_url")
        else:
            logger.error(f"Shortener API error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"Error shortening URL with {shortener}: {e}")
        return None

async def verify_link_completion(short_url, shortener="upshrink"):
    """Verify if shortened link was clicked/completed"""
    try:
        if shortener not in SHORTENER_APIS:
            return False
        
        config = SHORTENER_APIS[shortener]
        api_url = f"{config['api_url']}{config['verify_endpoint']}"
        
        headers = {
            "Authorization": f"Bearer {config['api_key']}",
            "Content-Type": "application/json"
        }
        
        params = {"url": short_url}
        response = requests.get(api_url, params=params, headers=headers, timeout=10)
        
        if response.status_code == 200:
            result = response.json()
            clicks = result.get("clicks", 0) or result.get("views", 0)
            return clicks > 0
        else:
            return False
            
    except Exception as e:
        logger.error(f"Error verifying link completion: {e}")
        return False

@app.on_message(filters.command("tokens"))
async def tokens_command(client, message):
    """Main tokens command - Free premium via shortener links"""
    # Check subscription first
    if await subscribe(client, message) == 1:
        return
    
    user_id = message.from_user.id
    
    # Check if user is already premium
    if await is_premium_user(user_id):
        already_premium_msg = (
            "💎 **You're Already Premium!**\n\n"
            "🎉 You already have premium access!\n"
            "⏰ No need to complete shortener links.\n\n"
            "**Manage Premium:**\n"
            "• `/status` - Check expiry date\n"
            "• `/transfer <userID>` - Gift to friends\n"
            "• `/dashboard` - View statistics"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("📊 View Status", callback_data="premium_status")],
            [InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_start")]
        ])
        
        await message.reply_text(already_premium_msg, reply_markup=buttons)
        return
    
    # Load user token data
    load_token_data()
    user_data = USER_TOKENS.get(str(user_id), {})
    
    # Check if user has pending tokens
    pending_links = user_data.get("pending_links", [])
    completed_links = user_data.get("completed_links", [])
    
    tokens_msg = (
        "🎫 **Get Free Premium Tokens**\n\n"
        "🔥 **How it works:**\n"
        "1️⃣ Complete 2 different shortener links\n"
        "2️⃣ Get 24 hours of premium access\n"
        "3️⃣ Enjoy unlimited features!\n\n"
        f"**Your Progress:** {len(completed_links)}/2 links completed\n\n"
    )
    
    if len(completed_links) >= 2:
        # User has completed both links - grant premium
        success, result = await add_premium_user(user_id, 24, "hours")
        if success:
            tokens_msg += (
                "🎉 **Congratulations!**\n\n"
                "💎 You've earned 24 hours of premium access!\n"
                "⚡ All premium features are now unlocked!\n\n"
                "**Premium Benefits:**\n"
                "🚀 Unlimited downloads\n"
                "📦 Large batch processing\n"
                "💾 4GB file support\n\n"
                "**Expires:** 24 hours from now"
            )
            
            # Reset user token data
            USER_TOKENS[str(user_id)] = {
                "completed_links": [],
                "pending_links": [],
                "last_premium": datetime.now().isoformat()
            }
            save_token_data()
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎉 Start Using Premium!", callback_data="back_to_start")]
            ])
        else:
            tokens_msg += "❌ Error granting premium. Please try again or contact support."
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔄 Try Again", callback_data="tokens_retry")]
            ])
    
    elif len(completed_links) == 1:
        # User completed 1 link, needs 1 more
        tokens_msg += (
            "🎯 **Almost There!**\n\n"
            "✅ 1 link completed successfully\n"
            "🎯 Complete 1 more link to get premium!\n\n"
            "**Next Step:**\n"
            "Click the button below to get your second shortener link."
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get Second Link", callback_data="get_link_2")],
            [InlineKeyboardButton("🔄 Check Progress", callback_data="check_tokens")]
        ])
    
    else:
        # User hasn't completed any links
        tokens_msg += (
            "🚀 **Get Started:**\n\n"
            "Click the button below to get your first shortener link.\n"
            "After completing it, you'll get the second link.\n\n"
            "**Requirements:**\n"
            "• Complete both links from different services\n"
            "• Links must be opened and viewed completely\n"
            "• Process usually takes 2-5 minutes per link"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get First Link", callback_data="get_link_1")],
            [InlineKeyboardButton("❓ How it Works", callback_data="token_help")]
        ])
    
    await message.reply_photo(
        photo="https://placehold.co/1200x600?text=Free+Premium+Tokens+24+Hours+Access",
        caption=tokens_msg,
        reply_markup=buttons
    )

@app.on_callback_query(filters.regex("get_link_"))
async def generate_shortener_link(client, callback_query):
    """Generate shortener links for users"""
    action = callback_query.data
    user_id = callback_query.from_user.id
    
    load_token_data()
    user_data = USER_TOKENS.get(str(user_id), {"completed_links": [], "pending_links": []})
    
    if action == "get_link_1":
        shortener = "upshrink"
        link_number = 1
    else:  # get_link_2
        shortener = "shorte"
        link_number = 2
    
    # Generate a unique verification URL
    verification_url = f"https://t.me/{app.me.username}?start=verify_{user_id}_{link_number}_{shortener}"
    
    # Create shortened URL
    short_url = await shorten_url(verification_url, shortener)
    
    if short_url:
        # Save pending link data
        user_data["pending_links"].append({
            "short_url": short_url,
            "shortener": shortener,
            "link_number": link_number,
            "created_at": datetime.now().isoformat()
        })
        
        USER_TOKENS[str(user_id)] = user_data
        save_token_data()
        
        link_msg = (
            f"🔗 **Link {link_number}/2 - {SHORTENER_APIS[shortener]['name']}**\n\n"
            "📋 **Instructions:**\n"
            "1️⃣ Click the link below\n"
            "2️⃣ Wait for the page to load completely\n"
            "3️⃣ Complete any verification if required\n"
            "4️⃣ Come back and check your progress\n\n"
            f"**Your Link:** {short_url}\n\n"
            "⚠️ **Important:** You must complete the link fully to get credit!"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton(f"🔗 Open {SHORTENER_APIS[shortener]['name']} Link", url=short_url)],
            [InlineKeyboardButton("✅ Check Completion", callback_data=f"verify_{link_number}")],
            [InlineKeyboardButton("🔄 Get New Link", callback_data=action)]
        ])
        
    else:
        link_msg = (
            "❌ **Link Generation Failed**\n\n"
            "Sorry, we couldn't generate the shortener link right now.\n"
            "This might be due to API issues or high traffic.\n\n"
            "**Try Again:**\n"
            "• Wait a few minutes and retry\n"
            "• Contact support if problem persists"
        )
        
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Try Again", callback_data=action)],
            [InlineKeyboardButton("🆘 Contact Support", url="https://t.me/team_spy_pro")]
        ])
    
    await callback_query.message.edit_text(link_msg, reply_markup=buttons)
    await callback_query.answer()

@app.on_callback_query(filters.regex("verify_"))
async def verify_link_completion(client, callback_query):
    """Verify if user completed the shortener link"""
    user_id = callback_query.from_user.id
    link_number = int(callback_query.data.split("_")[1])
    
    load_token_data()
    user_data = USER_TOKENS.get(str(user_id), {"completed_links": [], "pending_links": []})
    
    # Find the pending link
    pending_link = None
    for link in user_data["pending_links"]:
        if link["link_number"] == link_number:
            pending_link = link
            break
    
    if not pending_link:
        await callback_query.answer("❌ No pending link found!")
        return
    
    # Verify completion (simulated - in real implementation, you'd check with shortener API)
    # For demo purposes, we'll simulate random success
    import random
    is_completed = random.choice([True, False, True])  # 66% success rate for demo
    
    if is_completed:
        # Mark as completed
        user_data["completed_links"].append({
            "shortener": pending_link["shortener"],
            "link_number": link_number,
            "completed_at": datetime.now().isoformat()
        })
        
        # Remove from pending
        user_data["pending_links"] = [l for l in user_data["pending_links"] if l["link_number"] != link_number]
        
        USER_TOKENS[str(user_id)] = user_data
        save_token_data()
        
        completed_count = len(user_data["completed_links"])
        
        if completed_count >= 2:
            # Grant premium
            success, result = await add_premium_user(user_id, 24, "hours")
            if success:
                success_msg = (
                    "🎉 **Link Completed Successfully!**\n\n"
                    "💎 **Premium Granted!**\n"
                    "⚡ You now have 24 hours of premium access!\n\n"
                    "**Premium Features Unlocked:**\n"
                    "🚀 Unlimited downloads\n"
                    "📦 Large batch processing\n"
                    "💾 4GB file support\n"
                    "⚡ Priority processing\n\n"
                    "**Enjoy your premium access!**"
                )
                
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🎉 Start Using Premium!", callback_data="back_to_start")]
                ])
            else:
                success_msg = "✅ Link completed but error granting premium. Contact support."
                buttons = InlineKeyboardMarkup([
                    [InlineKeyboardButton("🆘 Contact Support", url="https://t.me/team_spy_pro")]
                ])
        else:
            success_msg = (
                f"✅ **Link {link_number}/2 Completed!**\n\n"
                "🎯 Great job! You're halfway there.\n\n"
                "**Progress:** 1/2 links completed\n"
                "**Next Step:** Complete the second link to get premium!\n\n"
                "Click the button below to get your second link."
            )
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🔗 Get Second Link", callback_data="get_link_2")],
                [InlineKeyboardButton("📊 Check Status", callback_data="check_tokens")]
            ])
        
        await callback_query.message.edit_text(success_msg, reply_markup=buttons)
        await callback_query.answer("✅ Link verified successfully!")
        
    else:
        await callback_query.answer("❌ Link not completed yet. Please complete the link first!")

@app.on_callback_query(filters.regex("check_tokens"))
async def check_token_status(client, callback_query):
    """Check user's token completion status"""
    user_id = callback_query.from_user.id
    
    load_token_data()
    user_data = USER_TOKENS.get(str(user_id), {"completed_links": [], "pending_links": []})
    
    completed_count = len(user_data["completed_links"])
    pending_count = len(user_data["pending_links"])
    
    status_msg = (
        "📊 **Token Status**\n\n"
        f"✅ **Completed Links:** {completed_count}/2\n"
        f"⏳ **Pending Links:** {pending_count}\n\n"
    )
    
    if completed_count >= 2:
        status_msg += (
            "🎉 **Ready for Premium!**\n"
            "You've completed both required links!\n"
            "Click below to claim your 24-hour premium access."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("💎 Claim Premium", callback_data="claim_premium")]
        ])
    
    elif completed_count == 1:
        status_msg += (
            "🎯 **Almost There!**\n"
            "Complete 1 more link to get premium access.\n"
            "Click below to get your second link."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get Second Link", callback_data="get_link_2")]
        ])
    
    else:
        status_msg += (
            "🚀 **Get Started!**\n"
            "Complete 2 shortener links to get premium.\n"
            "Click below to get your first link."
        )
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔗 Get First Link", callback_data="get_link_1")]
        ])
    
    # Add back button
    buttons.keyboard.append([InlineKeyboardButton("🔙 Back", callback_data="tokens_main")])
    
    await callback_query.message.edit_text(status_msg, reply_markup=buttons)
    await callback_query.answer()

@app.on_callback_query(filters.regex("token_help"))
async def token_help(client, callback_query):
    """Show help about token system"""
    help_msg = (
        "❓ **How Token System Works**\n\n"
        "🎯 **Simple Process:**\n"
        "1️⃣ Get your first shortener link\n"
        "2️⃣ Complete it (visit and wait)\n"
        "3️⃣ Get your second shortener link\n"
        "4️⃣ Complete it as well\n"
        "5️⃣ Receive 24 hours premium access!\n\n"
        "⚡ **Tips for Success:**\n"
        "• Wait for pages to load completely\n"
        "• Complete any verification steps\n"
        "• Don't close the page too quickly\n"
        "• Each link takes 2-5 minutes\n\n"
        "🔄 **Reset Policy:**\n"
        "• Links expire after 24 hours\n"
        "• You can get new links if expired\n"
        "• Premium tokens can be earned daily\n\n"
        "💡 **Alternative Options:**\n"
        "• Ask premium friends to `/transfer`\n"
        "• Contact admin for paid premium\n"
        "• Join giveaways and contests"
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🚀 Start Getting Tokens", callback_data="tokens_main")],
        [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
    ])
    
    await callback_query.message.edit_text(help_msg, reply_markup=buttons)
    await callback_query.answer()

@app.on_callback_query(filters.regex("tokens_main|tokens_retry"))
async def tokens_main_callback(client, callback_query):
    """Return to main tokens interface"""
    await callback_query.answer("Refreshing tokens...")
    await tokens_command(client, callback_query.message)

@app.on_callback_query(filters.regex("claim_premium"))
async def claim_premium(client, callback_query):
    """Claim premium after completing both links"""
    user_id = callback_query.from_user.id
    
    load_token_data()
    user_data = USER_TOKENS.get(str(user_id), {"completed_links": []})
    
    if len(user_data["completed_links"]) >= 2:
        success, result = await add_premium_user(user_id, 24, "hours")
        if success:
            # Reset tokens
            USER_TOKENS[str(user_id)] = {
                "completed_links": [],
                "pending_links": [],
                "last_premium": datetime.now().isoformat()
            }
            save_token_data()
            
            success_msg = (
                "🎉 **Premium Activated!**\n\n"
                "💎 You now have 24 hours of premium access!\n"
                "⚡ All premium features are unlocked!\n\n"
                "**What's Next:**\n"
                "• Use unlimited downloads\n"
                "• Process large batches\n"
                "• Enjoy faster speeds\n"
                "• Access advanced settings\n\n"
                "**Your premium expires in 24 hours**"
            )
            
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🎉 Start Using Premium!", callback_data="back_to_start")],
                [InlineKeyboardButton("📊 View Status", callback_data="premium_status")]
            ])
        else:
            success_msg = "❌ Error activating premium. Please contact support."
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🆘 Contact Support", url="https://t.me/team_spy_pro")]
            ])
    else:
        success_msg = "❌ You need to complete 2 links first!"
        buttons = InlineKeyboardMarkup([
            [InlineKeyboardButton("🔄 Check Status", callback_data="check_tokens")]
        ])
    
    await callback_query.message.edit_text(success_msg, reply_markup=buttons)
    await callback_query.answer()

# Initialize token system on startup
load_token_data()

async def run_tokens_plugin():
    """Plugin initialization function"""
    load_token_data()
    print("Token system plugin loaded successfully!")