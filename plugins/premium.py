# Copyright (c) 2025 Gagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# Enhanced Premium Management System by BlackBox AI

from shared_client import client as bot_client, app
from telethon import events
from datetime import timedelta, datetime
from config import OWNER_ID
from utils.func import add_premium_user, is_private_chat, is_premium_user, get_premium_details
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton as IK, InlineKeyboardMarkup as IKM, CallbackQuery
from config import OWNER_ID, JOIN_LINK as JL , ADMIN_CONTACT as AC
import base64 as spy
from utils.func import a1, a2, a3, a4, a5, a7, a8, a9, a10, a11
from plugins.start import subscribe
import json
import os

# Premium management tracking
PREMIUM_STATS_FILE = "premium_stats.json"
PREMIUM_STATS = {}

def load_premium_stats():
    """Load premium statistics"""
    global PREMIUM_STATS
    try:
        if os.path.exists(PREMIUM_STATS_FILE):
            with open(PREMIUM_STATS_FILE, 'r') as f:
                PREMIUM_STATS = json.load(f)
    except Exception as e:
        print(f"Error loading premium stats: {e}")
        PREMIUM_STATS = {}

def save_premium_stats():
    """Save premium statistics"""
    try:
        with open(PREMIUM_STATS_FILE, 'w') as f:
            json.dump(PREMIUM_STATS, f, indent=2, default=str)
    except Exception as e:
        print(f"Error saving premium stats: {e}")

def update_premium_stats(action, user_id=None, details=None):
    """Update premium statistics"""
    today = datetime.now().strftime("%Y-%m-%d")
    
    if "daily" not in PREMIUM_STATS:
        PREMIUM_STATS["daily"] = {}
    if today not in PREMIUM_STATS["daily"]:
        PREMIUM_STATS["daily"][today] = {
            "new_premium": 0,
            "expired_premium": 0,
            "transfers": 0,
            "token_activations": 0
        }
    
    if action in PREMIUM_STATS["daily"][today]:
        PREMIUM_STATS["daily"][today][action] += 1
    
    if "total" not in PREMIUM_STATS:
        PREMIUM_STATS["total"] = {
            "premium_users": 0,
            "total_activations": 0,
            "revenue_generated": 0
        }
    
    if action == "new_premium":
        PREMIUM_STATS["total"]["premium_users"] += 1
        PREMIUM_STATS["total"]["total_activations"] += 1
    
    save_premium_stats()

@bot_client.on(events.NewMessage(pattern='/add'))
async def add_premium_handler(event):
    """Enhanced /add command with better UI and tracking"""
    if not await is_private_chat(event):
        await event.respond(
            '🔒 **Security Notice**\n\n'
            'This command can only be used in private chats for security reasons.\n'
            'Please message the bot directly.'
        )
        return
    
    user_id = event.sender_id
    if user_id not in OWNER_ID:
        await event.respond(
            '🚫 **Access Denied**\n\n'
            '❌ This command is restricted to bot administrators only.\n'
            '👑 Only owners can manage premium subscriptions.\n\n'
            '**Support:** @team_spy_pro'
        )
        return
    
    text = event.message.text.strip()
    parts = text.split(' ')
    
    if len(parts) != 4:
        help_msg = (
            '📋 **Add Premium User - Command Format**\n\n'
            '**Usage:** `/add <user_id> <duration> <unit>`\n\n'
            '**Examples:**\n'
            '• `/add 123456789 1 day`\n'
            '• `/add 123456789 7 days`\n'
            '• `/add 123456789 1 month`\n'
            '• `/add 123456789 1 year`\n\n'
            '**Valid Units:**\n'
            '`min`, `hours`, `days`, `weeks`, `month`, `year`, `decades`\n\n'
            '**Tips:**\n'
            '• Use `/get` to see all user IDs\n'
            '• Premium users get unlimited access\n'
            '• System will notify the user automatically'
        )
        await event.respond(help_msg)
        return
    
    try:
        target_user_id = int(parts[1])
        duration_value = int(parts[2])
        duration_unit = parts[3].lower()
        
        valid_units = ['min', 'hours', 'days', 'weeks', 'month', 'year', 'decades']
        if duration_unit not in valid_units:
            await event.respond(
                f'❌ **Invalid Duration Unit**\n\n'
                f'Choose from: {", ".join(valid_units)}\n\n'
                '**Example:** `/add 123456 7 days`'
            )
            return
        
        # Check if user already has premium
        current_premium = await is_premium_user(target_user_id)
        status_msg = await event.respond('🔄 **Processing Premium Addition...**')
        
        success, result = await add_premium_user(target_user_id, duration_value, duration_unit)
        
        if success:
            expiry_utc = result
            expiry_ist = expiry_utc + timedelta(hours=5, minutes=30)
            formatted_expiry = expiry_ist.strftime('%d-%b-%Y %I:%M:%S %p')
            
            # Update statistics
            update_premium_stats("new_premium", target_user_id)
            
            success_msg = f'''
✅ **Premium Added Successfully!**

👤 **User:** `{target_user_id}`
⏰ **Duration:** {duration_value} {duration_unit}
📅 **Expires:** {formatted_expiry} (IST)
💎 **Status:** {"Renewed" if current_premium else "New Premium"}

📊 **Premium Benefits Activated:**
🚀 Unlimited downloads
📦 Large batch processing (500 files)
⚡ Priority queue processing
💾 4GB file upload support
🎯 Advanced customization options

**User will be notified automatically.**
            '''
            
            await status_msg.edit(success_msg)
            
            # Enhanced user notification
            try:
                user_notification = f'''
🎉 **Premium Access Granted!**

💎 **Congratulations!** You now have premium access to Save Restricted Content Bot!

⏰ **Your Premium Details:**
**Expires:** {formatted_expiry} (IST)
**Type:** {"Premium Renewal" if current_premium else "New Premium Member"}

🚀 **Your New Benefits:**
✅ **Unlimited Downloads** - No daily limits
✅ **Large Batches** - Process up to 500 files
✅ **Priority Processing** - 50% faster speeds  
✅ **4GB File Support** - Upload large files
✅ **Advanced Settings** - Full customization
✅ **Premium Support** - Priority help

🎯 **Get Started:**
• Use `/start` for the premium dashboard
• Try `/batch` for bulk processing
• Access `/settings` for advanced options

**Welcome to the premium experience!** 💎
                '''
                
                await bot_client.send_message(target_user_id, user_notification)
            except Exception as e:
                await event.respond(f'✅ Premium added but notification failed: {str(e)[:50]}')
        else:
            await status_msg.edit(f'❌ **Failed to add premium user**\n\n**Error:** {result}')
            
    except ValueError:
        await event.respond(
            '❌ **Invalid Input**\n\n'
            'User ID and duration must be valid numbers.\n\n'
            '**Example:** `/add 123456789 7 days`'
        )
    except Exception as e:
        await event.respond(f'❌ **System Error:** {str(e)[:100]}')

@bot_client.on(events.NewMessage(pattern='/rem'))
async def remove_premium_handler(event):
    """Enhanced premium removal with better tracking"""
    if not await is_private_chat(event):
        await event.respond('🔒 This command requires private chat for security.')
        return
    
    user_id = event.sender_id
    if user_id not in OWNER_ID:
        await event.respond('🚫 Access denied. Admin only command.')
        return
    
    text = event.message.text.strip()
    parts = text.split(' ')
    
    if len(parts) != 2:
        await event.respond(
            '📋 **Remove Premium User**\n\n'
            '**Usage:** `/rem <user_id>`\n\n'
            '**Example:** `/rem 123456789`'
        )
        return
    
    try:
        target_user_id = int(parts[1])
        
        # Check if user has premium
        if not await is_premium_user(target_user_id):
            await event.respond(
                f'❌ **User Not Premium**\n\n'
                f'User `{target_user_id}` does not have premium access.'
            )
            return
        
        # Remove premium (using database operation)
        from utils.func import premium_users_collection
        result = await premium_users_collection.delete_one({"user_id": target_user_id})
        
        if result.deleted_count > 0:
            success_msg = f'''
✅ **Premium Removed Successfully**

👤 **User:** `{target_user_id}`
🗑️ **Action:** Premium access revoked
⏰ **Effective:** Immediately

**User will be notified of the change.**
            '''
            
            await event.respond(success_msg)
            
            # Notify user
            try:
                user_notification = '''
📋 **Premium Access Update**

⚠️ Your premium access has been revoked by an administrator.

🔄 **What this means:**
• Limited to free user features
• Reduced download limits
• Standard processing speed

💡 **Get Premium Again:**
• Use `/tokens` for free premium
• Contact admin for paid premium
• Ask friends to `/transfer` premium

**Questions?** Contact @team_spy_pro
                '''
                await bot_client.send_message(target_user_id, user_notification)
            except:
                pass
        else:
            await event.respond('❌ Failed to remove premium access.')
            
    except ValueError:
        await event.respond('❌ Invalid user ID. Must be a number.')
    except Exception as e:
        await event.respond(f'❌ Error: {str(e)}')

@app.on_message(filters.command("transfer"))
async def transfer_premium(client, message):
    """Enhanced premium transfer with better UI"""
    if await subscribe(client, message) == 1:
        return
    
    sender_id = message.from_user.id
    
    # Check if sender has premium
    if not await is_premium_user(sender_id):
        no_premium_msg = '''
❌ **Premium Required**

🚫 You need premium access to transfer premium to others.

💡 **Get Premium:**
• Use `/tokens` for free 24h premium
• Contact admin for paid premium
• Join premium giveaways

**Why Transfer Premium?**
Gift premium access to friends and family!
        '''
        
        buttons = IKM([
            [IK("🎫 Get Free Tokens", callback_data="tokens_main")],
            [IK("💎 Premium Plans", callback_data="action_premium")]
        ])
        
        await message.reply_text(no_premium_msg, reply_markup=buttons)
        return
    
    args = message.text.split()
    if len(args) < 2:
        transfer_help = '''
🎁 **Transfer Premium to Others**

**Usage:** `/transfer <user_id> [hours]`

**Examples:**
• `/transfer 123456789` (Transfer 24 hours)
• `/transfer 123456789 48` (Transfer 48 hours)

**Notes:**
• Default transfer is 24 hours
• You need premium to transfer
• Recipient will be notified
• You keep your remaining premium

**Get User ID:**
Forward a message from the user to @userinfobot
        '''
        
        await message.reply_text(transfer_help)
        return
    
    try:
        target_user_id = int(args[1])
        transfer_hours = int(args[2]) if len(args) > 2 else 24
        
        # Validate transfer hours (reasonable limits)
        if transfer_hours > 168 or transfer_hours < 1:  # Max 1 week
            await message.reply_text(
                '❌ **Invalid Duration**\n\n'
                'Transfer duration must be between 1-168 hours (1 week max)'
            )
            return
        
        # Check if target already has premium
        target_has_premium = await is_premium_user(target_user_id)
        
        # Process transfer
        success, result = await add_premium_user(target_user_id, transfer_hours, "hours")
        
        if success:
            expiry = result.strftime('%d-%b-%Y %I:%M:%S %p')
            
            success_msg = f'''
🎁 **Premium Transfer Successful!**

✅ **Transferred:** {transfer_hours} hours premium
👤 **To User:** `{target_user_id}`
📅 **Expires:** {expiry}
💎 **Status:** {"Extended" if target_has_premium else "New Premium"}

**The recipient has been notified!** 🎉
            '''
            
            await message.reply_text(success_msg)
            
            # Notify recipient
            try:
                recipient_msg = f'''
🎉 **Premium Gift Received!**

💝 You've received {transfer_hours} hours of premium access as a gift!

👤 **From:** User ID `{sender_id}`
⏰ **Duration:** {transfer_hours} hours
📅 **Expires:** {expiry}

🚀 **Your Premium Benefits:**
✅ Unlimited downloads
✅ Large batch processing
✅ Priority processing
✅ 4GB file support
✅ Advanced settings

**Start enjoying your premium access!**
Use `/start` to access premium features.
                '''
                
                await client.send_message(target_user_id, recipient_msg)
            except:
                await message.reply_text('✅ Transfer completed but recipient notification failed.')
        else:
            await message.reply_text(f'❌ Transfer failed: {result}')
            
    except ValueError:
        await message.reply_text('❌ Invalid user ID. Must be a number.')
    except Exception as e:
        await message.reply_text(f'❌ Transfer error: {str(e)[:100]}')

@app.on_message(filters.command("status"))
async def premium_status(client, message):
    """Enhanced premium status with detailed info"""
    if await subscribe(client, message) == 1:
        return
    
    user_id = message.from_user.id
    is_premium = await is_premium_user(user_id)
    
    if is_premium:
        premium_details = await get_premium_details(user_id)
        
        if premium_details:
            start_date = premium_details.get('subscription_start')
            end_date = premium_details.get('subscription_end')
            
            start_str = start_date.strftime("%Y-%m-%d %H:%M") if start_date else "Unknown"
            end_str = end_date.strftime("%Y-%m-%d %H:%M") if end_date else "Lifetime"
            
            # Calculate remaining time
            if end_date:
                remaining = end_date - datetime.now()
                if remaining.total_seconds() > 0:
                    days = remaining.days
                    hours = remaining.seconds // 3600
                    minutes = (remaining.seconds % 3600) // 60
                    remaining_str = f"{days}d {hours}h {minutes}m"
                else:
                    remaining_str = "Expired"
            else:
                remaining_str = "Lifetime"
            
            status_msg = f'''
💎 **Premium Status - Active**

📊 **Subscription Details:**
**Status:** ✅ Active Premium Member
**Started:** {start_str}
**Expires:** {end_str}
**Remaining:** {remaining_str}

🚀 **Active Benefits:**
✅ Unlimited downloads
✅ Batch processing (500 files)
✅ Priority queue (50% faster)
✅ 4GB file uploads
✅ Advanced customization
✅ Premium support

💡 **Premium Actions:**
• Use `/transfer <userID>` to gift premium
• Use `/dashboard` for detailed stats
• Use `/settings` for advanced options
            '''
        else:
            status_msg = "💎 **Premium Active** but details unavailable."
    
    else:
        status_msg = '''
🆓 **Free User Status**

📊 **Current Plan:** Free User
⏰ **Premium:** Not Active
📥 **Download Limit:** Limited per day

💡 **Upgrade to Premium:**
🎫 **Free Method:** Use `/tokens` (24h premium)
💰 **Paid Method:** Contact admin for premium
🎁 **Gift Method:** Ask premium users to `/transfer`

🚀 **Premium Benefits You're Missing:**
❌ Limited downloads vs Unlimited
❌ Standard speed vs 50% faster
❌ Small batches vs 500 files
❌ Basic settings vs Advanced options
❌ Standard support vs Premium support

**Ready to upgrade?**
        '''
    
    buttons = []
    if is_premium:
        buttons = IKM([
            [IK("🎁 Transfer Premium", callback_data="transfer_premium")],
            [IK("📊 View Dashboard", callback_data="refresh_dashboard")]
        ])
    else:
        buttons = IKM([
            [IK("🎫 Get Free Premium", callback_data="tokens_main")],
            [IK("💎 Premium Plans", callback_data="action_premium")]
        ])
    
    await message.reply_text(status_msg, reply_markup=buttons)

@app.on_message(filters.command("premium"))
async def premium_info(client, message):
    """Enhanced premium information command"""
    if await subscribe(client, message) == 1:
        return
    
    user_id = message.from_user.id
    is_premium_user_flag = await is_premium_user(user_id)
    
    premium_msg = f'''
💎 **Premium Access Information**

{"🎉 **You're Premium!**" if is_premium_user_flag else "🔥 **Unlock Premium Features!**"}

🚀 **Premium Benefits:**
✅ **Unlimited Downloads** - No daily limits
✅ **Faster Processing** - 50% speed boost
✅ **Large Batches** - Up to 500 files at once
✅ **4GB File Support** - Handle massive files
✅ **Advanced Settings** - Full customization
✅ **Priority Support** - Faster help response
✅ **Auto-Resume** - Never lose progress

💰 **Premium Options:**

🎫 **FREE Premium (24 hours):**
• Complete 2 shortener links
• Instant activation
• Full premium features
• Renewable daily

💸 **Paid Premium:**
• Starting from $2 / ₹200
• Various duration options
• Payment via Amazon Gift Cards
• Instant activation

🎁 **Gift Premium:**
• Receive from premium friends
• Use `/transfer` command
• Share premium access

{"📊 **Your Premium Status:** Active ✅" if is_premium_user_flag else "📊 **Your Status:** Free User 🆓"}
    '''
    
    buttons = []
    if is_premium_user_flag:
        buttons = IKM([
            [IK("📊 Premium Status", callback_data="premium_status")],
            [IK("🎁 Transfer to Friend", callback_data="transfer_premium")],
            [IK("📈 View Dashboard", callback_data="refresh_dashboard")]
        ])
    else:
        buttons = IKM([
            [IK("🎫 Get Free 24h Premium", callback_data="tokens_main")],
            [IK("💰 Buy Premium", url=AC)],
            [IK("📋 Premium Plans", callback_data="see_plan")]
        ])
    
    await message.reply_photo(
        photo="https://placehold.co/1200x800?text=Premium+Access+Unlimited+Features+Fast+Processing",
        caption=premium_msg,
        reply_markup=buttons
    )

# Callback handlers for premium features
@app.on_callback_query(filters.regex("premium_status"))
async def premium_status_callback(client, callback_query):
    """Handle premium status callback"""
    await callback_query.answer("Checking premium status...")
    await premium_status(client, callback_query.message)

@app.on_callback_query(filters.regex("transfer_premium"))  
async def transfer_premium_callback(client, callback_query):
    """Handle transfer premium callback"""
    transfer_msg = '''
🎁 **Transfer Premium to Others**

**How to Transfer:**
Use command: `/transfer <user_id> [hours]`

**Examples:**
• `/transfer 123456789` - Transfer 24 hours
• `/transfer 123456789 48` - Transfer 48 hours

**Requirements:**
• You must have premium access
• Maximum 168 hours (1 week) per transfer
• Recipient will be notified immediately

**Get User ID:**
Forward any message from the user to @userinfobot

**Ready to make someone's day?** 💝
    '''
    
    buttons = IKM([
        [IK("❓ How to Get User ID", callback_data="get_userid_help")],
        [IK("🔙 Back", callback_data="action_premium")]
    ])
    
    await callback_query.message.edit_text(transfer_msg, reply_markup=buttons)
    await callback_query.answer()

@app.on_callback_query(filters.regex("get_userid_help"))
async def get_userid_help(client, callback_query):
    """Help for getting user IDs"""
    help_msg = '''
🆔 **How to Get Someone's User ID**

**Method 1 - Using @userinfobot:**
1. Forward any message from the person to @userinfobot
2. The bot will show their User ID
3. Copy the number (without spaces)

**Method 2 - Using Username:**
• If they have a username, you can try using @username
• But User ID is more reliable

**Method 3 - Ask Them:**
• Ask them to send `/start` to any info bot
• They can share their ID with you

**Example User ID:**
`123456789` (just numbers, no @ symbol)

**Security Note:**
Only transfer premium to people you trust!
    '''
    
    buttons = IKM([
        [IK("🔙 Back to Transfer", callback_data="transfer_premium")]
    ])
    
    await callback_query.message.edit_text(help_msg, reply_markup=buttons)
    await callback_query.answer()

# Load premium stats on startup
load_premium_stats()

attr1 = spy.b64encode("photo".encode()).decode()
attr2 = spy.b64encode("file_id".encode()).decode()

@app.on_message(filters.command(spy.b64decode(a5.encode()).decode()))
async def start_handler_premium(client, message):
    """Enhanced start handler with premium integration"""
    subscription_status = await subscribe(client, message)
    if subscription_status == 1:
        return

    b1 = spy.b64decode(a1).decode()
    b2 = int(spy.b64decode(a2).decode())
    b3 = spy.b64decode(a3).decode()
    b4 = spy.b64decode(a4).decode()
    b6 = spy.b64decode(a7).decode()
    b7 = spy.b64decode(a8).decode()
    b8 = spy.b64decode(a9).decode()
    b9 = spy.b64decode(a10).decode()
    b10 = spy.b64decode(a11).decode()

    try:
        tm = await getattr(app, b3)(b1, b2)
        pb = getattr(tm, spy.b64decode(attr1.encode()).decode())
        fd = getattr(pb, spy.b64decode(attr2.encode()).decode())

        kb = IKM([
            [IK(b7, url=JL)],
            [IK(b8, url=AC)]
        ])

        await getattr(message, b4)(
            fd,
            caption=b6,
            reply_markup=kb
        )
    except Exception as e:
        print(f"Enhanced start handler error: {e}")

async def run_premium_plugin():
    """Plugin initialization function"""
    load_premium_stats()
    print("Enhanced Premium management plugin loaded successfully!")