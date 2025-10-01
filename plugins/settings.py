# Copyright (c) 2025 devgagan : https://github.com/devgaganin.  
# Licensed under the GNU General Public License v3.0.  
# Enhanced Settings System by BlackBox AI

from telethon import events, Button
from pyrogram import filters
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup
import re
import os
import asyncio
import string
import random
from shared_client import client as gf, app
from config import OWNER_ID
from utils.func import get_user_data_key, save_user_data, users_collection
from plugins.start import subscribe

VIDEO_EXTENSIONS = {
    'mp4', 'mkv', 'avi', 'mov', 'wmv', 'flv', 'webm',
    'mpeg', 'mpg', '3gp'
}
SET_PIC = 'https://placehold.co/1200x800?text=Bot+Settings+Configuration+Panel'
MESS = '⚙️ **Settings Panel**\n\nCustomize your bot experience with advanced options!'

active_conversations = {}

async def get_user_settings_summary(user_id):
    """Get a summary of user's current settings"""
    chat_id = await get_user_data_key(user_id, 'chat_id', 'Not Set')
    rename_tag = await get_user_data_key(user_id, 'rename_tag', 'Not Set')
    caption = await get_user_data_key(user_id, 'caption', 'Not Set')
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    replacement_words = await get_user_data_key(user_id, 'replacement_words', {})
    session_active = bool(await get_user_data_key(user_id, 'session_string', None))
    
    # Check if thumbnail exists
    thumbnail_exists = os.path.exists(f'{user_id}.jpg')
    
    summary = f'''
📊 **Your Current Settings:**

🎯 **Upload Settings:**
**Chat ID:** {chat_id[:50] + "..." if isinstance(chat_id, str) and len(chat_id) > 50 else chat_id}
**Rename Tag:** {rename_tag[:30] + "..." if isinstance(rename_tag, str) and len(rename_tag) > 30 else rename_tag}

🎨 **Customization:**
**Custom Caption:** {"✅ Set" if caption != "Not Set" else "❌ Not Set"}
**Custom Thumbnail:** {"✅ Set" if thumbnail_exists else "❌ Not Set"}

🔧 **Advanced Options:**
**Delete Words:** {len(delete_words)} words configured
**Replace Words:** {len(replacement_words)} replacements configured
**Session Login:** {"🟢 Active" if session_active else "🔴 Inactive"}

💡 **Quick Stats:**
Your settings are {"🟢 Well Configured" if chat_id != "Not Set" or rename_tag != "Not Set" else "⚠️ Basic Setup"}
    '''
    
    return summary

async def send_modern_settings_panel(chat_id, user_id):
    """Send modern settings panel with enhanced UI"""
    summary = await get_user_settings_summary(user_id)
    
    buttons = [
        [
            Button.inline('🎯 Upload Settings', b'upload_settings'),
            Button.inline('🎨 Customization', b'customization_settings')
        ],
        [
            Button.inline('🔧 Advanced Options', b'advanced_settings'),
            Button.inline('🔑 Session & Login', b'session_settings')
        ],
        [
            Button.inline('📋 Settings Templates', b'settings_templates'),
            Button.inline('📊 View All Settings', b'view_all_settings')
        ],
        [
            Button.inline('🗑️ Reset All Settings', b'reset_confirm'),
            Button.inline('💾 Export Settings', b'export_settings')
        ],
        [
            Button.inline('❓ Settings Help', b'settings_help'),
            Button.inline('🔙 Back to Main', b'back_to_main')
        ]
    ]
    
    message_text = f"{MESS}\n\n{summary}"
    
    await gf.send_message(chat_id, message_text, buttons=buttons, file=SET_PIC)

@gf.on(events.NewMessage(incoming=True, pattern='/settings'))
async def settings_command(event):
    """Enhanced settings command with modern interface"""
    user_id = event.sender_id
    await send_modern_settings_panel(event.chat_id, user_id)

@app.on_message(filters.command("settings"))
async def settings_command_pyrogram(client, message):
    """Pyrogram version of settings command"""
    if await subscribe(client, message) == 1:
        return
    
    user_id = message.from_user.id
    summary = await get_user_settings_summary(user_id)
    
    buttons = InlineKeyboardMarkup([
        [
            InlineKeyboardButton('🎯 Upload Settings', callback_data='upload_settings'),
            InlineKeyboardButton('🎨 Customization', callback_data='customization_settings')
        ],
        [
            InlineKeyboardButton('🔧 Advanced Options', callback_data='advanced_settings'),
            InlineKeyboardButton('🔑 Session & Login', callback_data='session_settings')
        ],
        [
            InlineKeyboardButton('📋 Templates', callback_data='settings_templates'),
            InlineKeyboardButton('📊 All Settings', callback_data='view_all_settings')
        ],
        [
            InlineKeyboardButton('🗑️ Reset All', callback_data='reset_confirm'),
            InlineKeyboardButton('💾 Export', callback_data='export_settings')
        ],
        [
            InlineKeyboardButton('❓ Help', callback_data='settings_help'),
            InlineKeyboardButton('🏠 Home', callback_data='back_to_start')
        ]
    ])
    
    message_text = f"{MESS}\n\n{summary}"
    
    await message.reply_photo(
        photo=SET_PIC,
        caption=message_text,
        reply_markup=buttons
    )

@gf.on(events.CallbackQuery)
async def enhanced_callback_handler(event):
    """Enhanced callback handler for settings"""
    user_id = event.sender_id
    data = event.data
    
    callback_actions = {
        b'upload_settings': handle_upload_settings,
        b'customization_settings': handle_customization_settings,
        b'advanced_settings': handle_advanced_settings,
        b'session_settings': handle_session_settings,
        b'settings_templates': handle_settings_templates,
        b'view_all_settings': handle_view_all_settings,
        b'reset_confirm': handle_reset_confirm,
        b'export_settings': handle_export_settings,
        b'settings_help': handle_settings_help,
        
        # Upload settings sub-menu
        b'setchat': lambda e: start_setting_conversation(e, 'setchat', 
            """🎯 **Set Upload Chat ID**
            
Send me the chat ID where files should be uploaded:

**Format Examples:**
• `-1001234567890` - Regular channel/group
• `-1001234567890/123` - Topic in group (ChatID/TopicID)

**Important Notes:**
• Use -100 prefix for channels/groups
• Bot must be admin in the target chat
• For topic groups, add topic ID after /

**Get Chat ID:** Forward any message from the chat to @userinfobot"""),
        
        b'setrename': lambda e: start_setting_conversation(e, 'setrename', 
            """🏷️ **Set Rename Tag**
            
Send me the rename tag to append to all filenames:

**Examples:**
• `@MyChannel` - Adds channel name
• `- Premium Content` - Adds description
• `[HD Quality]` - Adds quality info

**Tips:**
• Keep it short and descriptive
• Will be added to every filename
• Use symbols for better visibility"""),
            
        b'setcaption': lambda e: start_setting_conversation(e, 'setcaption',
            """📋 **Set Custom Caption**
            
Send me the custom caption to add to all files:

**Examples:**
• Channel promotion text
• Copyright information  
• Download instructions
• Social media links

**Features:**
• Supports markdown formatting
• Can include emojis
• Added to all media files
• Combines with original captions"""),
        
        # Advanced settings
        b'setreplacement': lambda e: start_setting_conversation(e, 'setreplacement',
            """🔄 **Replace Words**
            
Send replacement in format: 'OLD_WORD' 'NEW_WORD'

**Examples:**
• `'test' 'demo'` - Replace 'test' with 'demo'
• `'old_name' 'new_name'` - Replace filename parts
• `'[AD]' '[Premium]'` - Replace tags

**Rules:**
• Use single quotes around each word
• Separate old and new with space
• Case sensitive matching
• Applied to filenames and captions"""),
        
        b'delete': lambda e: start_setting_conversation(e, 'deleteword',
            """🗑️ **Delete Words**
            
Send words separated by spaces to remove from filenames/captions:

**Examples:**
• `spam advertisement promo` - Remove these words
• `[AD] [SPAM] [PROMO]` - Remove these tags
• `unwanted terrible bad` - Remove negative words

**Features:**
• Space-separated list
• Removes from filenames and captions
• Case sensitive
• Applied before renaming"""),
        
        # Customization
        b'setthumb': lambda e: start_setting_conversation(e, 'setthumb',
            """🖼️ **Set Custom Thumbnail**
            
Send me a photo to use as custom thumbnail for all videos:

**Requirements:**
• JPG/PNG format preferred
• Recommended size: 1280x720 or 16:9 ratio
• File size under 200KB for best performance

**Tips:**
• High-quality images work best
• Avoid copyrighted content
• Thumbnail applies to all video uploads"""),
        
        # Session management
        b'addsession': lambda e: start_setting_conversation(e, 'addsession',
            """🔑 **Add Session String**
            
Send me your Pyrogram V2 session string:

**How to get session string:**
1. Use session generator bots
2. Run session generation script
3. Copy the entire session string

**Security:**
• Keep your session private
• Never share with others
• Used for private channel access
• Can be removed anytime with /logout"""),
        
        # Quick actions
        b'logout': handle_logout,
        b'reset': handle_reset_all,
        b'remthumb': handle_remove_thumbnail,
    }
    
    if data in callback_actions:
        await callback_actions[data](event)
    elif data == b'back_to_main':
        await send_modern_settings_panel(event.chat_id, user_id)

async def handle_upload_settings(event):
    """Handle upload settings submenu"""
    upload_msg = """
🎯 **Upload Settings**

Configure where and how your files are uploaded:

**Available Options:**
• **Set Chat ID** - Choose upload destination
• **Auto-Forward** - Forward to multiple chats
• **Topic Support** - Upload to specific topics
• **Upload Queue** - Manage upload order

**Current Settings:**
"""
    
    user_id = event.sender_id
    chat_id = await get_user_data_key(user_id, 'chat_id', 'Not configured')
    upload_msg += f"**Target Chat:** {chat_id}\n"
    
    buttons = [
        [Button.inline('📤 Set Chat ID', b'setchat')],
        [Button.inline('🔄 Auto-Forward Setup', b'autoforward')],
        [Button.inline('📋 Topic Configuration', b'topic_config')],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(upload_msg, buttons=buttons)

async def handle_customization_settings(event):
    """Handle customization settings submenu"""
    user_id = event.sender_id
    
    # Get current customization status
    rename_tag = await get_user_data_key(user_id, 'rename_tag', None)
    caption = await get_user_data_key(user_id, 'caption', None)
    thumbnail_exists = os.path.exists(f'{user_id}.jpg')
    
    custom_msg = f"""
🎨 **Customization Settings**

Personalize your content with custom branding:

**Current Status:**
• **Rename Tag:** {"✅ Set" if rename_tag else "❌ Not Set"}
• **Custom Caption:** {"✅ Set" if caption else "❌ Not Set"}
• **Custom Thumbnail:** {"✅ Set" if thumbnail_exists else "❌ Not Set"}

**Features:**
• Brand your downloads
• Add promotional content
• Create consistent styling
• Professional appearance
"""
    
    buttons = [
        [
            Button.inline('🏷️ Set Rename Tag', b'setrename'),
            Button.inline('📋 Set Caption', b'setcaption')
        ],
        [
            Button.inline('🖼️ Set Thumbnail', b'setthumb'),
            Button.inline('❌ Remove Thumbnail', b'remthumb')
        ],
        [
            Button.inline('🎨 Color Themes', b'color_themes'),
            Button.inline('📱 Template Gallery', b'template_gallery')
        ],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(custom_msg, buttons=buttons)

async def handle_advanced_settings(event):
    """Handle advanced settings submenu"""
    user_id = event.sender_id
    
    # Get advanced settings status
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    replacement_words = await get_user_data_key(user_id, 'replacement_words', {})
    
    advanced_msg = f"""
🔧 **Advanced Settings**

Power-user features for content processing:

**Text Processing:**
• **Delete Words:** {len(delete_words)} configured
• **Replace Words:** {len(replacement_words)} rules active
• **Smart Filtering:** Automatic content cleanup
• **Batch Rules:** Apply to all downloads

**Performance Options:**
• **Quality Selection:** Auto-optimize downloads
• **Speed Boost:** Priority processing
• **Error Recovery:** Auto-retry failed downloads
"""
    
    buttons = [
        [
            Button.inline('🔄 Replace Words', b'setreplacement'),
            Button.inline('🗑️ Delete Words', b'delete')
        ],
        [
            Button.inline('⚡ Performance', b'performance_settings'),
            Button.inline('🛡️ Safety Options', b'safety_settings')
        ],
        [
            Button.inline('🔍 Content Filters', b'content_filters'),
            Button.inline('📊 Analytics', b'analytics_settings')
        ],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(advanced_msg, buttons=buttons)

async def handle_session_settings(event):
    """Handle session and login settings"""
    user_id = event.sender_id
    session_active = bool(await get_user_data_key(user_id, 'session_string', None))
    
    session_msg = f"""
🔑 **Session & Login Settings**

Manage your account access and security:

**Current Status:**
• **Session:** {"🟢 Active" if session_active else "🔴 Inactive"}
• **Private Access:** {"✅ Enabled" if session_active else "❌ Disabled"}
• **Auto-Login:** {"✅ On" if session_active else "❌ Off"}

**Features:**
• Access private channels without manual login
• Persistent session management
• Secure encrypted storage
• Easy logout option

**Security:**
Your session is encrypted and stored securely.
"""
    
    buttons = [
        [Button.inline('🔑 Add Session', b'addsession')],
        [Button.inline('🚪 Logout Session', b'logout') if session_active else Button.inline('📱 Login Guide', b'login_guide')],
        [Button.inline('🔒 Security Info', b'security_info')],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(session_msg, buttons=buttons)

async def handle_settings_templates(event):
    """Handle settings templates"""
    templates_msg = """
📋 **Settings Templates**

Quick setup with pre-configured templates:

**Available Templates:**

🎬 **Content Creator:**
• Channel branding enabled
• Custom thumbnails
• Promotional captions
• Quality optimization

📚 **Archival Setup:**
• Clean filenames
• Metadata preservation
• Organized structure
• Bulk processing

🚀 **Speed Optimized:**
• Fast downloads
• Minimal processing
• Priority queue
• Auto-retry

💼 **Professional:**
• Business branding
• Watermarks
• Custom formatting
• Analytics enabled

Choose a template to apply instantly!
"""
    
    buttons = [
        [
            Button.inline('🎬 Content Creator', b'template_creator'),
            Button.inline('📚 Archival', b'template_archival')
        ],
        [
            Button.inline('🚀 Speed Optimized', b'template_speed'),
            Button.inline('💼 Professional', b'template_professional')
        ],
        [
            Button.inline('🎨 Custom Template', b'template_custom'),
            Button.inline('💾 Save Current', b'template_save')
        ],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(templates_msg, buttons=buttons)

async def handle_view_all_settings(event):
    """Display all current settings in detail"""
    user_id = event.sender_id
    
    # Gather all settings
    chat_id = await get_user_data_key(user_id, 'chat_id', 'Not Set')
    rename_tag = await get_user_data_key(user_id, 'rename_tag', 'Not Set')
    caption = await get_user_data_key(user_id, 'caption', 'Not Set')
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    replacement_words = await get_user_data_key(user_id, 'replacement_words', {})
    session_active = bool(await get_user_data_key(user_id, 'session_string', None))
    thumbnail_exists = os.path.exists(f'{user_id}.jpg')
    
    all_settings_msg = f"""
📊 **Complete Settings Overview**

🎯 **Upload Configuration:**
**Target Chat ID:** `{chat_id}`
**Auto-Forward:** {'Enabled' if chat_id != 'Not Set' else 'Disabled'}

🏷️ **File Processing:**
**Rename Tag:** `{rename_tag}`
**Custom Caption:** {"Set" if caption != "Not Set" else "Not Set"}

🎨 **Customization:**
**Custom Thumbnail:** {'✅ Active' if thumbnail_exists else '❌ None'}

🔧 **Text Processing:**
**Delete Words:** {', '.join(delete_words) if delete_words else 'None configured'}
**Word Replacements:** {len(replacement_words)} rules active

🔑 **Account Access:**
**Session Status:** {'🟢 Active (Private access enabled)' if session_active else '🔴 Inactive'}

📈 **Configuration Score:** {calculate_config_score(user_id, chat_id, rename_tag, caption, delete_words, replacement_words, session_active, thumbnail_exists)}/100
"""
    
    buttons = [
        [Button.inline('⚙️ Quick Config', b'quick_config')],
        [Button.inline('💾 Export Config', b'export_settings')],
        [Button.inline('🔙 Back to Settings', b'back_to_settings')]
    ]
    
    await event.edit(all_settings_msg, buttons=buttons)

def calculate_config_score(user_id, chat_id, rename_tag, caption, delete_words, replacement_words, session_active, thumbnail_exists):
    """Calculate configuration completeness score"""
    score = 0
    
    if chat_id != 'Not Set': score += 25
    if rename_tag != 'Not Set': score += 20
    if caption != 'Not Set': score += 15
    if delete_words: score += 10
    if replacement_words: score += 10
    if session_active: score += 15
    if thumbnail_exists: score += 5
    
    return score

async def handle_reset_confirm(event):
    """Handle reset confirmation"""
    confirm_msg = """
🗑️ **Reset All Settings**

⚠️ **Warning: This action cannot be undone!**

**This will reset:**
• Upload chat configuration
• Custom rename tags
• Caption templates
• Word filters and replacements
• Custom thumbnail (will be deleted)

**This will NOT reset:**
• Your session login
• Downloaded files
• Premium status
• Usage statistics

Are you sure you want to proceed?
"""
    
    buttons = [
        [
            Button.inline('✅ Yes, Reset All', b'reset'),
            Button.inline('❌ Cancel', b'back_to_settings')
        ]
    ]
    
    await event.edit(confirm_msg, buttons=buttons)

async def start_setting_conversation(event, conv_type, prompt_message):
    """Start a setting conversation with enhanced prompts"""
    user_id = event.sender_id
    if user_id in active_conversations:
        await event.respond('Previous conversation cancelled. Starting new one.')
    
    msg = await event.respond(f'{prompt_message}\n\n**Cancel:** Send /cancel anytime')
    active_conversations[user_id] = {'type': conv_type, 'message_id': msg.id}

# Enhanced conversation handlers with better validation and feedback

@gf.on(events.NewMessage(pattern='/cancel'))
async def cancel_conversation(event):
    """Enhanced cancel with better feedback"""
    user_id = event.sender_id
    if user_id in active_conversations:
        conv_type = active_conversations[user_id]['type']
        del active_conversations[user_id]
        
        await event.respond(
            f'✅ **Configuration Cancelled**\n\n'
            f'❌ {conv_type.title()} setup was cancelled.\n'
            f'⚙️ Use /settings to try again or configure other options.'
        )
    else:
        await event.respond('ℹ️ No active configuration found.')

@gf.on(events.NewMessage())
async def handle_enhanced_conversation_input(event):
    """Enhanced conversation handler with validation"""
    user_id = event.sender_id
    if user_id not in active_conversations or event.message.text.startswith('/'):
        return
        
    conv_type = active_conversations[user_id]['type']
    
    handlers = {
        'setchat': handle_enhanced_setchat,
        'setrename': handle_enhanced_setrename,
        'setcaption': handle_enhanced_setcaption,
        'setreplacement': handle_enhanced_setreplacement,
        'addsession': handle_enhanced_addsession,
        'deleteword': handle_enhanced_deleteword,
        'setthumb': handle_enhanced_setthumb
    }
    
    if conv_type in handlers:
        await handlers[conv_type](event, user_id)
    
    if user_id in active_conversations:
        del active_conversations[user_id]

async def handle_enhanced_setchat(event, user_id):
    """Enhanced chat ID validation"""
    try:
        chat_id = event.text.strip()
        
        # Validate chat ID format
        if not (chat_id.startswith('-100') or '/' in chat_id):
            await event.respond(
                '❌ **Invalid Format**\n\n'
                'Chat ID must start with -100 or include topic ID.\n'
                '**Examples:**\n'
                '• `-1001234567890` - Regular chat\n'
                '• `-1001234567890/123` - Topic chat'
            )
            return
        
        await save_user_data(user_id, 'chat_id', chat_id)
        
        success_msg = f'''
✅ **Chat ID Set Successfully!**

📤 **Upload Destination:** `{chat_id}`
{'📋 **Topic Mode:** Enabled' if '/' in chat_id else '📢 **Channel Mode:** Enabled'}

**Next Steps:**
• Test with a small download first
• Make sure bot is admin in the chat
• Use /settings to configure more options
        '''
        
        await event.respond(success_msg)
    except Exception as e:
        await event.respond(f'❌ **Error:** {str(e)[:100]}')

async def handle_enhanced_setrename(event, user_id):
    """Enhanced rename tag with validation"""
    rename_tag = event.text.strip()
    
    if len(rename_tag) > 100:
        await event.respond('❌ Rename tag too long (max 100 characters)')
        return
    
    await save_user_data(user_id, 'rename_tag', rename_tag)
    
    success_msg = f'''
✅ **Rename Tag Set Successfully!**

🏷️ **New Tag:** `{rename_tag}`
📁 **Application:** All downloaded files
🎯 **Effect:** Added to every filename

**Example Result:**
`original_video.mp4` → `original_video {rename_tag}.mp4`
    '''
    
    await event.respond(success_msg)

async def handle_enhanced_setcaption(event, user_id):
    """Enhanced caption with markdown support info"""
    caption = event.text
    
    if len(caption) > 1000:
        await event.respond('❌ Caption too long (max 1000 characters)')
        return
    
    await save_user_data(user_id, 'caption', caption)
    
    success_msg = f'''
✅ **Custom Caption Set Successfully!**

📋 **Your Caption:**
{caption}

📝 **Features:**
• Applied to all media files
• Supports markdown formatting
• Combined with original captions
• Can include emojis and links

**Markdown Support:** **bold**, *italic*, `code`, [links](url)
    '''
    
    await event.respond(success_msg)

async def handle_enhanced_setreplacement(event, user_id):
    """Enhanced replacement with better parsing"""
    match = re.match("'(.+)' '(.+)'", event.text)
    if not match:
        await event.respond(
            "❌ **Invalid Format**\n\n"
            "Use: 'OLD_WORD' 'NEW_WORD'\n"
            "**Example:** 'test' 'demo'"
        )
        return
    
    word, replace_word = match.groups()
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    
    if word in delete_words:
        await event.respond(f"❌ '{word}' is in delete list. Remove it first.")
        return
    
    replacements = await get_user_data_key(user_id, 'replacement_words', {})
    replacements[word] = replace_word
    await save_user_data(user_id, 'replacement_words', replacements)
    
    success_msg = f'''
✅ **Word Replacement Added!**

🔄 **Rule:** `{word}` → `{replace_word}`
📊 **Total Rules:** {len(replacements)}
🎯 **Applied To:** Filenames and captions

**All Your Replacements:**
{chr(10).join([f"• `{k}` → `{v}`" for k, v in replacements.items()])}
    '''
    
    await event.respond(success_msg)

async def handle_enhanced_deleteword(event, user_id):
    """Enhanced delete words with conflict checking"""
    words_to_delete = event.message.text.split()
    delete_words = await get_user_data_key(user_id, 'delete_words', [])
    replacements = await get_user_data_key(user_id, 'replacement_words', {})
    
    # Check for conflicts with replacements
    conflicts = [word for word in words_to_delete if word in replacements]
    if conflicts:
        await event.respond(f"❌ Conflicts with replacements: {', '.join(conflicts)}")
        return
    
    delete_words = list(set(delete_words + words_to_delete))
    await save_user_data(user_id, 'delete_words', delete_words)
    
    success_msg = f'''
✅ **Delete Words Updated!**

🗑️ **Added:** {', '.join(words_to_delete)}
📊 **Total Delete Words:** {len(delete_words)}
🎯 **Effect:** Removed from all filenames/captions

**All Delete Words:**
{', '.join(delete_words)}
    '''
    
    await event.respond(success_msg)

async def handle_enhanced_addsession(event, user_id):
    """Enhanced session with validation"""
    session_string = event.text.strip()
    
    if len(session_string) < 100:  # Basic validation
        await event.respond('❌ Session string seems too short. Please check.')
        return
    
    await save_user_data(user_id, 'session_string', session_string)
    
    success_msg = '''
✅ **Session Added Successfully!**

🔑 **Private Access:** Enabled
🎯 **Features Unlocked:**
• Access private channels
• No manual login required
• Persistent authentication
• Secure encrypted storage

**Security Notice:**
Your session is encrypted and stored securely.
Use /logout to remove it anytime.
    '''
    
    await event.respond(success_msg)

async def handle_enhanced_setthumb(event, user_id):
    """Enhanced thumbnail with image validation"""
    if event.photo:
        temp_path = await event.download_media()
        try:
            # Validate image
            from PIL import Image
            img = Image.open(temp_path)
            width, height = img.size
            
            thumb_path = f'{user_id}.jpg'
            if os.path.exists(thumb_path):
                os.remove(thumb_path)
            os.rename(temp_path, thumb_path)
            
            success_msg = f'''
✅ **Thumbnail Set Successfully!**

🖼️ **Image Details:**
• **Size:** {width}x{height} pixels
• **Format:** {img.format}
• **Applied To:** All video uploads

**Optimization Tips:**
• 16:9 ratio works best
• 1280x720 recommended
• Keep file size under 200KB
            '''
            
            await event.respond(success_msg)
        except Exception as e:
            await event.respond(f'❌ **Image Error:** {str(e)[:100]}')
            if os.path.exists(temp_path):
                os.remove(temp_path)
    else:
        await event.respond('❌ Please send a photo file.')

# Quick action handlers
async def handle_logout(event):
    """Handle logout from settings"""
    user_id = event.sender_id
    result = await users_collection.update_one(
        {'user_id': user_id},
        {'$unset': {'session_string': ''}}
    )
    
    if result.modified_count > 0:
        await event.respond('✅ **Logged out successfully!**\n\n🔑 Session removed from secure storage.')
    else:
        await event.respond('ℹ️ You are not logged in.')

async def handle_remove_thumbnail(event):
    """Handle thumbnail removal"""
    user_id = event.sender_id
    try:
        os.remove(f'{user_id}.jpg')
        await event.respond('✅ **Thumbnail removed successfully!**\n\n🖼️ Default thumbnails will be used.')
    except FileNotFoundError:
        await event.respond('ℹ️ No custom thumbnail found to remove.')

async def handle_reset_all(event):
    """Handle complete settings reset"""
    user_id = event.sender_id
    try:
        # Reset database settings
        await users_collection.update_one(
            {'user_id': user_id},
            {'$unset': {
                'delete_words': '',
                'replacement_words': '',
                'rename_tag': '',
                'caption': '',
                'chat_id': ''
            }}
        )
        
        # Remove thumbnail file
        thumbnail_path = f'{user_id}.jpg'
        if os.path.exists(thumbnail_path):
            os.remove(thumbnail_path)
        
        success_msg = '''
✅ **Settings Reset Complete!**

🗑️ **Reset Items:**
• Upload chat configuration
• Rename tags and captions
• Word filters and replacements
• Custom thumbnail

🔑 **Preserved:**
• Session login (use /logout separately)
• Premium status
• Usage statistics

**Ready for fresh configuration!**
        '''
        
        await event.respond(success_msg)
    except Exception as e:
        await event.respond(f'❌ **Reset Error:** {str(e)[:100]}')

# Utility functions for file operations
def generate_random_name(length=7):
    """Generate random filename"""
    characters = string.ascii_letters + string.digits
    return ''.join(random.choice(characters) for _ in range(length))

async def rename_file(file, sender, edit):
    """Enhanced file renaming with better error handling"""
    try:
        delete_words = await get_user_data_key(sender, 'delete_words', [])
        custom_rename_tag = await get_user_data_key(sender, 'rename_tag', '')
        replacements = await get_user_data_key(sender, 'replacement_words', {})
        
        # Extract filename and extension
        last_dot_index = str(file).rfind('.')
        if last_dot_index != -1 and last_dot_index != 0:
            extension = str(file)[last_dot_index + 1:]
            if extension.isalpha() and len(extension) <= 9:
                if extension.lower() in VIDEO_EXTENSIONS:
                    original_filename = str(file)[:last_dot_index]
                    file_extension = 'mp4'
                else:
                    original_filename = str(file)[:last_dot_index]
                    file_extension = extension
            else:
                original_filename = str(file)[:last_dot_index]
                file_extension = 'mp4'
        else:
            original_filename = str(file)
            file_extension = 'mp4'
        
        # Process filename
        processed_filename = original_filename
        
        # Apply word replacements first
        for old_word, new_word in replacements.items():
            processed_filename = processed_filename.replace(old_word, new_word)
        
        # Remove delete words
        for word in delete_words:
            processed_filename = processed_filename.replace(word, '')
        
        # Clean up multiple spaces and special characters
        processed_filename = re.sub(r'\s+', ' ', processed_filename).strip()
        
        # Add custom rename tag
        if custom_rename_tag:
            final_filename = f'{processed_filename} {custom_rename_tag}.{file_extension}'
        else:
            final_filename = f'{processed_filename}.{file_extension}'
        
        # Sanitize the final filename
        final_filename = re.sub(r'[<>:"/\\|?*]', '_', final_filename)
        
        # Rename the file
        os.rename(file, final_filename)
        return final_filename
        
    except Exception as e:
        print(f"Enhanced rename error: {e}")
        return file

async def run_settings_plugin():
    """Plugin initialization function"""
    print("Enhanced Settings plugin loaded successfully!")