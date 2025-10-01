# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# Enhanced by BlackBox AI with modern UI/UX improvements

from shared_client import app
from pyrogram import filters
from pyrogram.errors import UserNotParticipant
from pyrogram.types import BotCommand, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from config import LOG_GROUP, OWNER_ID, FORCE_SUB, JOIN_LINK, ADMIN_CONTACT
from utils.func import is_premium_user, get_premium_details
import time
from datetime import datetime

async def subscribe(app, message):
    """Enhanced subscription check with modern UI"""
    if FORCE_SUB:
        try:
            user = await app.get_chat_member(FORCE_SUB, message.from_user.id)
            if str(user.status) == "ChatMemberStatus.BANNED":
                banned_msg = (
                    "🚫 **Access Denied**\n\n"
                    "❌ You have been banned from using this bot.\n"
                    "📞 Contact our support team if you believe this is an error.\n\n"
                    "**Support:** @team_spy_pro"
                )
                await message.reply_text(banned_msg)
                return 1
        except UserNotParticipant:
            link = await app.export_chat_invite_link(FORCE_SUB)
            join_msg = (
                "🔐 **Channel Subscription Required**\n\n"
                "📢 To use this bot, you must join our official channel first.\n"
                "💎 Get access to exclusive updates and features!\n\n"
                "👇 **Click the button below to join**"
            )
            buttons = InlineKeyboardMarkup([
                [InlineKeyboardButton("🚀 Join Channel", url=link)],
                [InlineKeyboardButton("✅ Check Again", callback_data="check_subscription")]
            ])
            await message.reply_photo(
                photo="https://placehold.co/1200x600?text=Join+Our+Channel+for+Exclusive+Bot+Access",
                caption=join_msg, 
                reply_markup=buttons
            )
            return 1
        except Exception as ggn:
            error_msg = (
                "⚠️ **System Error**\n\n"
                "❌ Something went wrong while checking your subscription.\n"
                "🔄 Please try again in a moment.\n\n"
                f"**Error Details:** `{str(ggn)[:100]}`\n"
                "**Support:** @team_spy_pro"
            )
            await message.reply_text(error_msg)
            return 1
    return 0

@app.on_message(filters.command("start"))
async def start_handler(client, message):
    """Enhanced start command with modern dashboard"""
    subscription_check = await subscribe(client, message)
    if subscription_check == 1:
        return
    
    user = message.from_user
    user_id = user.id
    
    # Check premium status
    is_premium = await is_premium_user(user_id)
    premium_details = await get_premium_details(user_id) if is_premium else None
    
    # Create personalized welcome message
    welcome_text = f"""
🌟 **Welcome to Save Restricted Content Bot v3** 🌟

👋 Hello **{user.first_name}**! 

🚀 **What I Can Do:**
• 📥 **Extract** content from private/public channels
• 🎥 **Download** videos from 30+ platforms (YouTube, Instagram, etc.)
• 🎵 **Download** audio in high quality
• 📦 **Batch processing** for multiple files
• ⚙️ **Custom settings** and personalization
• 🔄 **Auto-forward** to your channels
• 🎨 **Custom thumbnails** and captions

{"💎 **PREMIUM USER** - Enjoy unlimited access!" if is_premium else "🆓 **Free User** - Upgrade for unlimited features!"}

🎯 **Quick Actions:**
"""
    
    # Create dynamic buttons based on user status
    buttons = []
    
    # Row 1 - Main Actions
    main_row = [
        InlineKeyboardButton("📥 Extract Single", callback_data="action_single"),
        InlineKeyboardButton("📦 Batch Extract", callback_data="action_batch")
    ]
    buttons.append(main_row)
    
    # Row 2 - Download Actions  
    download_row = [
        InlineKeyboardButton("🎥 Video Download", callback_data="action_video"),
        InlineKeyboardButton("🎵 Audio Download", callback_data="action_audio")
    ]
    buttons.append(download_row)
    
    # Row 3 - Settings & Account
    settings_row = [
        InlineKeyboardButton("⚙️ Settings", callback_data="action_settings"),
        InlineKeyboardButton("👤 Account", callback_data="action_account")
    ]
    buttons.append(settings_row)
    
    # Row 4 - Premium & Help
    help_row = [
        InlineKeyboardButton("💎 Premium" if not is_premium else "💎 Premium Info", callback_data="action_premium"),
        InlineKeyboardButton("❓ Help", callback_data="action_help")
    ]
    buttons.append(help_row)
    
    # Row 5 - Support & Updates
    support_row = [
        InlineKeyboardButton("🆘 Support", url=ADMIN_CONTACT),
        InlineKeyboardButton("📢 Updates", url=JOIN_LINK)
    ]
    buttons.append(support_row)
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    # Add premium status info
    if is_premium and premium_details:
        expiry = premium_details.get('subscription_end')
        if expiry:
            expiry_str = expiry.strftime("%Y-%m-%d %H:%M")
            welcome_text += f"\n💎 **Premium expires:** {expiry_str}"
    
    welcome_text += "\n\n🔥 **Get started by choosing an action below!**"
    
    await message.reply_photo(
        photo="https://placehold.co/1200x800?text=Save+Restricted+Content+Bot+v3+Dashboard",
        caption=welcome_text,
        reply_markup=keyboard
    )

@app.on_message(filters.command("set"))
async def set_commands(_, message):
    """Enhanced command setup for administrators"""
    if message.from_user.id not in OWNER_ID:
        unauthorized_msg = (
            "🚫 **Access Denied**\n\n"
            "❌ You are not authorized to use this command.\n"
            "👑 Only bot administrators can configure commands.\n\n"
            "**Support:** @team_spy_pro"
        )
        await message.reply(unauthorized_msg)
        return
     
    # Enhanced command list with better descriptions
    commands = [
        BotCommand("start", "🚀 Start the bot and view dashboard"),
        BotCommand("batch", "📦 Extract content in bulk"),
        BotCommand("single", "📥 Process single link"),
        BotCommand("login", "🔑 Login to access private channels"),
        BotCommand("logout", "🚪 Logout from your account"),
        BotCommand("setbot", "🤖 Add your custom bot"),
        BotCommand("rembot", "❌ Remove your custom bot"),
        BotCommand("dl", "🎥 Download videos from 30+ sites"),
        BotCommand("adl", "🎵 Download audio from 30+ sites"),
        BotCommand("settings", "⚙️ Customize bot settings"),
        BotCommand("dashboard", "📊 View user dashboard"),
        BotCommand("premium", "💎 Premium plans and status"),
        BotCommand("tokens", "🎫 Get free premium tokens"),
        BotCommand("transfer", "💝 Gift premium to others"),
        BotCommand("stats", "📈 View bot statistics"),
        BotCommand("help", "❓ Get help and support"),
        BotCommand("plan", "🗓️ View premium plans"),
        BotCommand("terms", "📋 Terms and conditions"),
        BotCommand("cancel", "🚫 Cancel current operation"),
        BotCommand("stop", "⛔ Stop batch process"),
        BotCommand("status", "🔄 Check premium status"),
        BotCommand("add", "➕ Add premium user (Admin)"),
        BotCommand("rem", "➖ Remove premium user (Admin)")
    ]
    
    await app.set_bot_commands(commands)
    
    success_msg = (
        "✅ **Commands Updated Successfully!**\n\n"
        f"📋 **Total Commands:** {len(commands)}\n"
        "🔄 **Updated:** All commands refreshed\n"
        "⚡ **Status:** Ready for use\n\n"
        "**Note:** Commands are now available in the bot menu!"
    )
    await message.reply(success_msg)

# Enhanced help system with modern design and better organization
help_pages = [
    {
        "title": "🚀 **Getting Started Guide**",
        "content": """
🌟 **Welcome to Save Restricted Content Bot v3!**

**🎯 Quick Start:**
1️⃣ **Join Channel** - Subscribe to our channel for updates
2️⃣ **Choose Action** - Use dashboard buttons or commands
3️⃣ **Login** (Optional) - For private channels access
4️⃣ **Start Extracting** - Send links or use batch mode

**🔥 Main Features:**
🎥 **Video Download** - From 30+ platforms
🎵 **Audio Download** - High-quality audio extraction  
📥 **Content Extraction** - Save restricted posts
📦 **Batch Processing** - Process multiple links
⚙️ **Custom Settings** - Personalize your experience
💎 **Premium Features** - Unlimited access

**💡 Tip:** Use the dashboard buttons for easier navigation!
        """
    },
    {
        "title": "📥 **Content Extraction Commands**",
        "content": """
**🔗 Single Link Processing:**
• Send any Telegram link directly
• Use `/single <link>` command
• Works with public channels instantly

**📦 Batch Processing:**
• `/batch` - Start batch extraction
• Process up to 500 files (premium)
• Resume interrupted downloads

**🔑 Login & Access:**
• `/login` - Access private channels
• `/logout` - Remove your session
• `/setbot <token>` - Add custom bot
• `/rembot` - Remove custom bot

**⚙️ Settings Control:**
• `/settings` - Open settings panel
• Set custom captions, thumbnails
• Configure auto-forward options
• Customize file renaming rules
        """
    },
    {
        "title": "🎥 **Download Commands**",
        "content": """
**🎬 Video Downloads:**
• `/dl <link>` - Download videos
• Supports YouTube, Instagram, Facebook
• Auto-quality selection (up to 4K)
• Progress tracking with ETA

**🎵 Audio Downloads:**
• `/adl <link>` - Extract audio only
• High-quality MP3 format
• Embedded metadata & thumbnails
• Perfect for music downloads

**🌐 Supported Platforms:**
✅ YouTube & YouTube Music
✅ Instagram (Posts & Stories)
✅ Facebook & Twitter
✅ TikTok & Snapchat
✅ And 25+ more platforms!

**💡 Pro Tips:**
- Use quality selection for specific formats
- Downloads work without login for public content
        """
    },
    {
        "title": "💎 **Premium & Account**",
        "content": """
**💎 Premium Benefits:**
🚀 **Unlimited Downloads** - No daily limits
⚡ **Faster Processing** - Priority queue
📦 **Large Batches** - Up to 500 files
🎯 **Advanced Settings** - More customization
💾 **4GB File Support** - Large file uploads
🔄 **Auto-Resume** - Never lose progress

**🎫 Get Free Premium:**
• `/tokens` - Get premium tokens
• Complete shortener links
• 24-hour free premium access
• Share with friends for bonuses

**👤 Account Management:**
• `/status` - Check premium status
• `/transfer <userID>` - Gift premium
• `/dashboard` - View your statistics
• `/premium` - Plans & pricing

**🔄 Free Token System:**
Complete 2 different shortener links = 24hrs premium!
        """
    },
    {
        "title": "⚙️ **Settings & Customization**",
        "content": """
**🎨 Visual Settings:**
• **Custom Thumbnails** - Set your own thumbnails
• **Caption Templates** - Personalized captions
• **File Renaming** - Auto-rename downloaded files
• **Watermarks** - Add custom watermarks

**🔄 Auto-Forward Settings:**
• **Set Chat ID** - Forward to channels/groups
• **Topic Support** - Forward to specific topics
• **Bulk Forward** - Mass forwarding options
• **Schedule Forward** - Time-based forwarding

**🛠️ Advanced Options:**
• **Replace Words** - Custom text replacement
• **Delete Words** - Remove unwanted text
• **Quality Settings** - Preferred download quality
• **Session Management** - Multiple account support

**📋 Quick Commands:**
`/settings` - Open settings panel
        """
    },
    {
        "title": "🛠️ **Admin & Advanced**",
        "content": """
**👑 Admin Commands (Owner Only):**
• `/add <userID> <time> <unit>` - Add premium user
• `/rem <userID>` - Remove premium access
• `/stats` - View bot statistics
• `/set` - Update bot commands
• `/broadcast` - Send announcements

**🔧 Advanced Features:**
• **API Integration** - Custom API support
• **Webhook Support** - External integrations
• **Database Backups** - Auto data protection
• **Error Logging** - Comprehensive logs
• **Rate Limiting** - Anti-spam protection

**🚨 Troubleshooting:**
• `/cancel` - Cancel current operation
• `/stop` - Stop batch processing
• `/help` - This help system
• Contact: @team_spy_pro

**📈 Bot Statistics:**
Check `/stats` for detailed usage analytics
        """
    }
]

async def send_help_page(message, page_number=0, edit=False):
    """Send or edit help page with navigation"""
    if page_number < 0 or page_number >= len(help_pages):
        return
    
    page = help_pages[page_number]
    
    # Navigation buttons
    buttons = []
    nav_row = []
    
    if page_number > 0:
        nav_row.append(InlineKeyboardButton("⬅️ Previous", callback_data=f"help_prev_{page_number}"))
    
    nav_row.append(InlineKeyboardButton(f"📄 {page_number + 1}/{len(help_pages)}", callback_data="help_noop"))
    
    if page_number < len(help_pages) - 1:
        nav_row.append(InlineKeyboardButton("Next ➡️", callback_data=f"help_next_{page_number}"))
    
    buttons.append(nav_row)
    
    # Quick action buttons
    quick_row = [
        InlineKeyboardButton("🏠 Home", callback_data="back_to_start"),
        InlineKeyboardButton("⚙️ Settings", callback_data="action_settings")
    ]
    buttons.append(quick_row)
    
    keyboard = InlineKeyboardMarkup(buttons)
    
    help_text = f"{page['title']}\n\n{page['content']}"
    
    if edit:
        await message.edit_text(help_text, reply_markup=keyboard)
    else:
        await message.reply_text(help_text, reply_markup=keyboard)

@app.on_message(filters.command("help"))
async def help_command(client, message):
    """Enhanced help command"""
    join = await subscribe(client, message)
    if join == 1:
        return
    
    await send_help_page(message, 0)

# Callback query handlers for interactive features
@app.on_callback_query(filters.regex(r"help_(prev|next)_(\d+)"))
async def help_navigation(client, callback_query):
    """Handle help page navigation"""
    action, page_number = callback_query.data.split("_")[1], int(callback_query.data.split("_")[2])
    
    if action == "prev":
        page_number -= 1
    elif action == "next":
        page_number += 1
    
    await send_help_page(callback_query.message, page_number, edit=True)
    await callback_query.answer()

@app.on_callback_query(filters.regex("action_"))
async def handle_dashboard_actions(client, callback_query: CallbackQuery):
    """Handle dashboard button actions"""
    action = callback_query.data.replace("action_", "")
    user_id = callback_query.from_user.id
    
    if action == "single":
        response_text = (
            "📥 **Single Link Extraction**\n\n"
            "🔗 Send me any Telegram link to extract content:\n\n"
            "**Supported Links:**\n"
            "• `https://t.me/channel/123` - Public channel\n"
            "• `https://t.me/c/123456/789` - Private channel\n"
            "• `https://t.me/bot/message_id` - Bot messages\n\n"
            "💡 **Tip:** For private channels, use `/login` first!"
        )
        
    elif action == "batch":
        response_text = (
            "📦 **Batch Extraction**\n\n"
            "🚀 Use `/batch` command to start bulk processing\n\n"
            "**Features:**\n"
            "• Process multiple messages at once\n"
            "• Resume interrupted downloads\n"
            "• Real-time progress tracking\n"
            f"• {'Unlimited' if await is_premium_user(user_id) else 'Limited'} batch size\n\n"
            "⚡ **Quick Start:** `/batch`"
        )
        
    elif action == "video":
        response_text = (
            "🎥 **Video Download**\n\n"
            "📺 Download videos from 30+ platforms!\n\n"
            "**Usage:** `/dl <link>`\n\n"
            "**Supported Sites:**\n"
            "✅ YouTube (up to 4K)\n"
            "✅ Instagram & Stories\n"
            "✅ Facebook & Twitter\n"
            "✅ TikTok & Snapchat\n"
            "✅ And many more!\n\n"
            "💡 **Example:** `/dl https://youtube.com/watch?v=...`"
        )
        
    elif action == "audio":
        response_text = (
            "🎵 **Audio Download**\n\n"
            "🎧 Extract high-quality audio from videos!\n\n"
            "**Usage:** `/adl <link>`\n\n"
            "**Features:**\n"
            "• High-quality MP3 format\n"
            "• Embedded metadata & thumbnails\n"
            "• Works with all video platforms\n"
            "• Perfect for music extraction\n\n"
            "💡 **Example:** `/adl https://youtube.com/watch?v=...`"
        )
        
    elif action == "settings":
        response_text = (
            "⚙️ **Settings Panel**\n\n"
            "🎨 Customize your bot experience!\n\n"
            "**Available Settings:**\n"
            "• Custom thumbnails & captions\n"
            "• File renaming rules\n"
            "• Auto-forward configuration\n"
            "• Quality preferences\n"
            "• Session management\n\n"
            "🔧 **Open Settings:** `/settings`"
        )
        
    elif action == "account":
        is_premium = await is_premium_user(user_id)
        premium_details = await get_premium_details(user_id) if is_premium else None
        
        status_emoji = "💎" if is_premium else "🆓"
        status_text = "Premium" if is_premium else "Free"
        
        response_text = f"""
👤 **Your Account**

**Status:** {status_emoji} {status_text}
**User ID:** `{user_id}`
        """
        
        if is_premium and premium_details:
            expiry = premium_details.get('subscription_end')
            if expiry:
                expiry_str = expiry.strftime("%Y-%m-%d %H:%M")
                response_text += f"\n**Premium Expires:** {expiry_str}"
        
        response_text += (
            "\n\n**Quick Actions:**\n"
            "• `/status` - Check premium status\n"
            "• `/dashboard` - View detailed stats\n"
            "• `/premium` - Upgrade to premium\n"
            "• `/tokens` - Get free premium tokens"
        )
        
    elif action == "premium":
        is_premium = await is_premium_user(user_id)
        
        if is_premium:
            response_text = (
                "💎 **Premium Account**\n\n"
                "🎉 You're already a premium user!\n\n"
                "**Your Benefits:**\n"
                "🚀 Unlimited downloads\n"
                "⚡ Priority processing\n"
                "📦 Large batch processing\n"
                "🎯 Advanced settings\n"
                "💾 4GB file support\n\n"
                "**Commands:**\n"
                "• `/status` - Check expiry\n"
                "• `/transfer <userID>` - Gift premium"
            )
        else:
            response_text = (
                "💎 **Get Premium Access**\n\n"
                "🔥 Unlock unlimited features!\n\n"
                "**Premium Benefits:**\n"
                "🚀 Unlimited downloads\n"
                "⚡ 50% faster processing\n"
                "📦 Batch up to 500 files\n"
                "💾 4GB file uploads\n"
                "🎯 Advanced customization\n\n"
                "**Get Premium:**\n"
                "🎫 `/tokens` - Free 24h premium\n"
                "💰 `/plan` - View pricing\n"
                "🎁 Ask friends for `/transfer`"
            )
    
    elif action == "help":
        await callback_query.answer("Opening help guide...")
        await send_help_page(callback_query.message, 0)
        return
    
    else:
        response_text = "🚧 **Feature Coming Soon**\n\nThis feature is under development!"
    
    buttons = [[InlineKeyboardButton("🔙 Back to Dashboard", callback_data="back_to_start")]]
    keyboard = InlineKeyboardMarkup(buttons)
    
    await callback_query.message.edit_text(response_text, reply_markup=keyboard)
    await callback_query.answer()

@app.on_callback_query(filters.regex("back_to_start"))
async def back_to_dashboard(client, callback_query):
    """Return to main dashboard"""
    await callback_query.answer("Returning to dashboard...")
    # Simulate start command
    await start_handler(client, callback_query.message)

@app.on_callback_query(filters.regex("check_subscription"))
async def check_subscription(client, callback_query):
    """Re-check subscription status"""
    try:
        user = await app.get_chat_member(FORCE_SUB, callback_query.from_user.id)
        if str(user.status) not in ["ChatMemberStatus.BANNED"]:
            await callback_query.answer("✅ Subscription verified! Welcome!")
            await start_handler(client, callback_query.message)
        else:
            await callback_query.answer("❌ Please join the channel first!")
    except UserNotParticipant:
        await callback_query.answer("❌ Please join the channel first!")
    except Exception as e:
        await callback_query.answer(f"Error: {str(e)[:50]}")

@app.on_message(filters.command("terms") & filters.private)
async def terms_command(client, message):
    """Enhanced terms and conditions"""
    terms_text = (
        "📜 **Terms and Conditions**\n\n"
        "✨ **Content Responsibility:**\n"
        "We are not responsible for user actions. Users are solely responsible for their content usage and compliance with copyright laws.\n\n"
        "⚡ **Service Availability:**\n"
        "We do not guarantee 100% uptime or service availability. Premium purchases do not guarantee uninterrupted service.\n\n"
        "🔒 **Account Management:**\n"
        "User authorization and account management are at our discretion. We reserve the right to modify or terminate accounts as needed.\n\n"
        "💳 **Premium Services:**\n"
        "Premium features are subject to availability and may change without notice. Refunds are handled on a case-by-case basis.\n\n"
        "📋 **Fair Usage:**\n"
        "Please use the bot responsibly and respect rate limits. Abuse of services may result in account suspension.\n\n"
        "🔄 **Updates:**\n"
        "These terms may be updated periodically. Continued use constitutes acceptance of updated terms."
    )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("💎 View Plans", callback_data="action_premium")],
        [InlineKeyboardButton("🆘 Contact Support", url=ADMIN_CONTACT)],
        [InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_start")]
    ])
    
    await message.reply_text(terms_text, reply_markup=buttons)

@app.on_message(filters.command("plan") & filters.private)
async def plan_command(client, message):
    """Enhanced premium plans"""
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)
    
    if is_premium:
        plan_text = (
            "💎 **You're Already Premium!**\n\n"
            "🎉 Enjoying all premium benefits!\n\n"
            "**Your Premium Features:**\n"
            "🚀 Unlimited downloads\n"
            "⚡ Priority processing queue\n"
            "📦 Batch up to 500 files\n"
            "💾 4GB file support\n"
            "🎯 Advanced customization\n"
            "🔄 Auto-resume downloads\n\n"
            "**Manage Premium:**\n"
            "• `/status` - Check expiry date\n"
            "• `/transfer <userID>` - Gift to friends\n"
            "• `/dashboard` - View statistics"
        )
    else:
        plan_text = (
            "💎 **Premium Plans**\n\n"
            "🔥 **Unlock Full Potential!**\n\n"
            "**💰 Pricing:**\n"
            "• Starting from $2 or ₹200\n"
            "• Payment via Amazon Gift Cards\n"
            "• Instant activation\n\n"
            "**🎁 Free Premium Options:**\n"
            "🎫 **Token System** - Complete 2 shortener links = 24hrs premium\n"
            "🤝 **Referrals** - Get premium through friends\n"
            "💝 **Transfers** - Receive from premium users\n\n"
            "**📦 Premium Benefits:**\n"
            "🚀 **Unlimited** downloads (Free: Limited)\n"
            "⚡ **50% faster** processing\n"
            "📦 **Batch up to 500** files (Free: Limited)\n"
            "💾 **4GB file support**\n"
            "🎯 **Advanced settings** & customization\n"
            "🔄 **Auto-resume** interrupted downloads\n"
            "💬 **Priority support**"
        )
    
    buttons = InlineKeyboardMarkup([
        [InlineKeyboardButton("🎫 Get Free Tokens", callback_data="action_premium")],
        [InlineKeyboardButton("💬 Contact for Premium", url=ADMIN_CONTACT)],
        [InlineKeyboardButton("📋 Terms & Conditions", callback_data="terms_callback")],
        [InlineKeyboardButton("🏠 Back to Home", callback_data="back_to_start")]
    ])
    
    await message.reply_text(plan_text, reply_markup=buttons)

@app.on_callback_query(filters.regex("terms_callback"))
async def terms_callback(client, callback_query):
    """Handle terms callback"""
    await terms_command(client, callback_query.message)

# Enhanced error handling for callback queries
@app.on_callback_query(filters.regex("help_noop"))
async def help_noop(client, callback_query):
    """Handle no-operation help callbacks"""
    await callback_query.answer()

async def run_start_plugin():
    """Plugin initialization function"""
    print("Enhanced Start plugin loaded successfully!")