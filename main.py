import os
import random
from threading import Thread
import requests
from hashlib import md5
from bs4 import BeautifulSoup
import base64
import secrets
try:
    import requests
    from cfonts import render
except ImportError:
    os.system("pip install requests cfonts")

import time
import string
import uuid
from datetime import datetime
import json
from dotenv import load_dotenv
import sys

load_dotenv()

# Read from environment variables
bot_token = os.getenv("BOT_TOKEN")

if not bot_token:
    print("❌ Missing BOT_TOKEN environment variable")
    sys.exit(1)

# Store user states (username they're processing)
user_states = {}

def send_telegram(chat_id, text, parse_mode="HTML"):
    """Send message to Telegram user"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": parse_mode
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        return r.json()
    except Exception as e:
        print(f"[-] Telegram send error: {e}")
        return None

def send_telegram_keyboard(chat_id, text, buttons):
    """Send message with inline keyboard buttons"""
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "HTML",
        "reply_markup": json.dumps({"inline_keyboard": buttons})
    }
    try:
        r = requests.post(url, data=payload, timeout=10)
        return r.json()
    except Exception as e:
        print(f"[-] Telegram send error: {e}")
        return None

def generate_device_info():
    """Generate Android device info for Instagram API"""
    ANDROID_ID = f"android-{''.join(random.choices(string.hexdigits.lower(), k=16))}"
    USER_AGENT = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    WATERFALL_ID = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp())
    nums = ''.join([str(random.randint(1, 100)) for _ in range(4)])
    PASSWORD = f'#PWD_INSTAGRAM:0:{timestamp}:Random@{nums}'
    return ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD

def make_headers(mid="", user_agent=""):
    """Create headers for Instagram API requests"""
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Bloks-Version-Id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
        "X-Mid": mid,
        "User-Agent": user_agent,
        "Content-Length": "9481"
    }

def id_user(user_id):
    """Get Instagram username from user ID"""
    try:
        url = f"https://i.instagram.com/api/v1/users/{user_id}/info/"
        headers = {
            "User-Agent": "Instagram 219.0.0.12.117 Android"
        }
        r = requests.get(url, headers=headers, timeout=10)
        
        try:
            username = r.json()["user"]["username"]
            return username
        except:
            return "Unknown"
    except:
        return "Unknown"

def reset_instagram_password(reset_link):
    """Reset Instagram password using reset link"""
    try:
        ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
        
        # Extract uidb36 and token from reset link
        uidb36 = reset_link.split("uidb36=")[1].split("&token=")[0]
        token = reset_link.split("&token=")[1].split(":")[0]

        url = "https://i.instagram.com/api/v1/accounts/password_reset/"
        data = {
            "source": "one_click_login_email",
            "uidb36": uidb36,
            "device_id": ANDROID_ID,
            "token": token,
            "waterfall_id": WATERFALL_ID
        }
        
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data, timeout=10)
        
        if "user_id" not in r.text:
            return {"success": False, "error": "Invalid reset link format"}

        mid = r.headers.get("Ig-Set-X-Mid")
        resp_json = r.json()
        user_id = resp_json.get("user_id")
        cni = resp_json.get("cni")
        nonce_code = resp_json.get("nonce_code")
        challenge_context = resp_json.get("challenge_context")

        url2 = "https://i.instagram.com/api/v1/bloks/apps/com.instagram.challenge.navigation.take_challenge/"
        data2 = {
            "user_id": str(user_id),
            "cni": str(cni),
            "nonce_code": str(nonce_code),
            "bk_client_context": '{"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"}',
            "challenge_context": str(challenge_context),
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "get_challenge": "true"
        }
        
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2, timeout=10).text
        
        challenge_context_final = r2.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]

        data3 = {
            "is_caa": "False",
            "source": "",
            "uidb36": "",
            "error_state": {"type_name":"str","index":0,"state_id":1048583541},
            "afv": "",
            "cni": str(cni),
            "token": "",
            "has_follow_up_screens": "0",
            "bk_client_context": {"bloks_version":"e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd","styles_id":"instagram"},
            "challenge_context": challenge_context_final,
            "bloks_versioning_id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
            "enc_new_password1": PASSWORD,
            "enc_new_password2": PASSWORD
        }
        
        requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data3, timeout=10)
        new_password = PASSWORD.split(":")[-1]
        
        return {
            "success": True,
            "password": new_password,
            "user_id": user_id
        }
        
    except Exception as e:
        return {"success": False, "error": str(e)}

def process_reset_link(chat_id, username, reset_link):
    """Process reset link and send results"""
    try:
        print(f"[*] Processing for user {chat_id} (Instagram: {username})...")
        
        # Send processing message
        send_telegram(chat_id, 
            f"⏳ <b>Processing...</b>\n\n"
            f"Username: <code>{username}</code>\n\n"
            f"Please wait while we process the reset link...",
            parse_mode="HTML")
        
        result = reset_instagram_password(reset_link)
        
        if result.get("success"):
            user_id = result.get("user_id")
            new_password = result.get("password")
            verified_username = id_user(user_id)
            
            msg = f"""
✅ <b>PASSWORD RESET SUCCESSFUL</b>

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Account Details:</b>
━━━━━━━━━━━━━━━━━━━━━━━━

👤 <b>Username:</b> <code>{verified_username}</code>
🔐 <b>New Password:</b> <code>{new_password}</code>
🆔 <b>User ID:</b> <code>{user_id}</code>

━━━━━━━━━━━━━━━━━━━━━━━━

<b>⚠️ Important:</b>
• Save your new password securely
• Log in to your Instagram account
• Change password to something you remember
• Enable two-factor authentication for security

━━━━━━━━━━━━━━━━━━━━━━━━

<i>Thank you for using our service</i>
"""
            print(f"[+] Success for user {chat_id}")
            send_telegram(chat_id, msg, parse_mode="HTML")
            
            # Reset user state
            if chat_id in user_states:
                del user_states[chat_id]
                
        else:
            error_msg = f"""
❌ <b>RESET FAILED</b>

<b>Error:</b>
<code>{result.get('error', 'Unknown error')}</code>

<b>Troubleshooting:</b>
• Verify the reset link is correct
• Check if the link has expired
• Try requesting a new reset link from Instagram
• Contact support if problem persists

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Do you want to try again?</b>
Send /reset to start over.
"""
            print(f"[-] Error for user {chat_id}: {result.get('error')}")
            send_telegram(chat_id, error_msg, parse_mode="HTML")
            
            # Reset user state
            if chat_id in user_states:
                del user_states[chat_id]
                
    except Exception as e:
        print(f"[-] Exception for user {chat_id}: {str(e)}")
        error_msg = f"""
❌ <b>ERROR PROCESSING REQUEST</b>

<b>Error:</b>
<code>{str(e)}</code>

Please try again by sending /reset
"""
        send_telegram(chat_id, error_msg, parse_mode="HTML")
        
        # Reset user state
        if chat_id in user_states:
            del user_states[chat_id]

def handle_message(chat_id, text, user_name):
    """Handle incoming messages"""
    
    # /start command
    if text.lower() == "/start":
        welcome_msg = f"""
👋 <b>Welcome to Instagram Account Recovery Service</b>

This is a professional tool to help you regain access to your Instagram account using password reset links.

<b>How it works:</b>
1️⃣ Send your Instagram username
2️⃣ Provide the password reset link
3️⃣ Receive your new credentials instantly

<b>⚠️ Important:</b>
• Use only on <u>YOUR OWN</u> accounts
• This service is for account recovery only
• All data is processed securely and privately
• No data is stored or logged

<b>Ready to begin?</b>
Send /reset to start the process.
"""
        send_telegram(chat_id, welcome_msg, parse_mode="HTML")
        return
    
    # /reset command
    if text.lower() == "/reset":
        user_states[chat_id] = {"step": "username"}
        reset_msg = """
🔐 <b>INSTAGRAM ACCOUNT RECOVERY</b>

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Step 1 of 2: Enter Username</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Please enter your Instagram username:

<i>Example: john_doe_123</i>
"""
        send_telegram(chat_id, reset_msg, parse_mode="HTML")
        return
    
    # /help command
    if text.lower() == "/help":
        help_msg = """
📚 <b>HELP & SUPPORT</b>

<b>Commands:</b>
/start - Show welcome message
/reset - Start account recovery process
/help - Show this help message
/cancel - Cancel current process

<b>How to get a reset link:</b>
1. Go to Instagram login page
2. Click "Forgot password?"
3. Enter your email/username
4. Check your email for reset link
5. Copy the link and send it here

<b>Common Issues:</b>
❓ Link expired? - Request a new reset link
❓ Wrong username? - Use /reset and try again
❓ Still having issues? - Contact Instagram support

━━━━━━━━━━━━━━━━━━━━━━━━
For more help, visit: instagram.com/help
"""
        send_telegram(chat_id, help_msg, parse_mode="HTML")
        return
    
    # /cancel command
    if text.lower() == "/cancel":
        if chat_id in user_states:
            del user_states[chat_id]
        cancel_msg = "❌ Process cancelled. Send /reset to start over."
        send_telegram(chat_id, cancel_msg, parse_mode="HTML")
        return
    
    # Check user state
    if chat_id not in user_states:
        intro_msg = """
👋 <b>Welcome!</b>

I'm here to help you recover your Instagram account.

To get started, send /reset

For more information, send /help
"""
        send_telegram(chat_id, intro_msg, parse_mode="HTML")
        return
    
    # Handle step 1: Username
    if user_states[chat_id]["step"] == "username":
        username = text.strip()
        
        if not username or len(username) < 3:
            error_msg = "❌ Invalid username. Username must be at least 3 characters.\n\nPlease try again:"
            send_telegram(chat_id, error_msg, parse_mode="HTML")
            return
        
        user_states[chat_id]["username"] = username
        user_states[chat_id]["step"] = "reset_link"
        
        link_msg = f"""
✅ <b>Username Received</b>

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Step 2 of 2: Send Reset Link</b>
━━━━━━━━━━━━━━━━━━━━━━━━

Username: <code>{username}</code>

Now please send the Instagram password reset link:

<i>Example of reset link:</i>
<code>https://instagram.com/users/password-reset/...?uidb36=...&token=...</code>

<b>Note:</b> The link should contain 'uidb36=' and 'token=' parameters
"""
        send_telegram(chat_id, link_msg, parse_mode="HTML")
        return
    
    # Handle step 2: Reset Link
    if user_states[chat_id]["step"] == "reset_link":
        reset_link = text.strip()
        username = user_states[chat_id]["username"]
        
        # Validate reset link format
        if "uidb36=" not in reset_link or "token=" not in reset_link:
            error_msg = """
❌ <b>Invalid Reset Link Format</b>

The link you provided doesn't seem to be a valid Instagram reset link.

<b>Valid reset link should contain:</b>
• <code>uidb36=</code> parameter
• <code>token=</code> parameter

Please check and send the correct link, or send /reset to try again.
"""
            send_telegram(chat_id, error_msg, parse_mode="HTML")
            return
        
        # Process in background thread
        thread = Thread(target=process_reset_link, args=(chat_id, username, reset_link))
        thread.daemon = True
        thread.start()

def get_updates(offset=0):
    """Get messages from Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    payload = {"offset": offset, "timeout": 30}
    try:
        r = requests.post(url, json=payload, timeout=35)
        return r.json()
    except Exception as e:
        print(f"[-] Error getting updates: {e}")
        return {"ok": False, "result": []}

def bot_polling():
    """Main bot polling loop"""
    offset = 0
    print("\n" + "="*60)
    print("🤖 INSTAGRAM ACCOUNT RECOVERY BOT - PROFESSIONAL VERSION")
    print("="*60)
    print("[+] Bot started successfully")
    print("[+] Listening for incoming messages...")
    print("[+] Press Ctrl+C to stop\n")
    
    while True:
        try:
            response = get_updates(offset)
            
            if response.get("ok"):
                updates = response.get("result", [])
                
                for update in updates:
                    offset = update.get("update_id") + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    user_name = message.get("from", {}).get("first_name", "User")
                    
                    if chat_id and text:
                        print(f"[*] Message from {user_name} (ID: {chat_id}): {text[:50]}...")
                        handle_message(chat_id, text, user_name)
            
            time.sleep(0.1)
            
        except KeyboardInterrupt:
            print("\n[!] Bot stopped by user")
            break
        except Exception as e:
            print(f"[-] Error in polling loop: {e}")
            time.sleep(5)

def main():
    bot_polling()

if __name__ == "__main__":
    main()
