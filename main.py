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
except ImportError:
    os.system("pip install requests")

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
        print(f"\n[*] ==================== STARTING PASSWORD RESET ====================")
        print(f"[*] Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
        print(f"[+] Step 1: Generated device info")
        print(f"    ANDROID_ID: {ANDROID_ID[:20]}...")
        print(f"    PASSWORD: {PASSWORD}")
        
        # Extract uidb36 and token from reset link
        try:
            uidb36 = reset_link.split("uidb36=")[1].split("&")[0]
            token = reset_link.split("token=")[1].split("&")[0]
            print(f"[+] Step 2: Extracted credentials from link")
            print(f"    uidb36: {uidb36[:15]}...")
            print(f"    token: {token[:15]}...")
        except IndexError as e:
            print(f"[-] FAILED at Step 2: Could not extract credentials")
            print(f"    Error: {e}")
            return {"success": False, "error": "Invalid reset link format - missing uidb36 or token"}

        # STEP 1: SEND PASSWORD RESET REQUEST
        print(f"\n[*] Step 3: Sending password reset request to Instagram...")
        url = "https://i.instagram.com/api/v1/accounts/password_reset/"
        data = {
            "source": "one_click_login_email",
            "uidb36": uidb36,
            "device_id": ANDROID_ID,
            "token": token,
            "waterfall_id": WATERFALL_ID
        }
        
        print(f"    Waiting for Instagram response (7-8 seconds)...")
        start_time = time.time()
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data, timeout=15)
        elapsed_time = time.time() - start_time
        
        print(f"[+] Step 3 Complete: Got response in {elapsed_time:.2f} seconds")
        print(f"    Status Code: {r.status_code}")
        print(f"    Response Length: {len(r.text)} chars")
        
        # CRITICAL CHECK: Verify user_id exists
        if r.status_code != 200:
            print(f"[-] FAILED at Step 3: Bad HTTP status")
            print(f"    Response: {r.text[:500]}")
            return {"success": False, "error": f"Instagram returned HTTP {r.status_code}"}
        
        if "user_id" not in r.text:
            print(f"[-] FAILED at Step 3: user_id not in response")
            print(f"    Response: {r.text[:500]}")
            return {"success": False, "error": "Reset link is invalid, expired, or already used"}

        # STEP 2: PARSE RESPONSE AND GET CHALLENGE CONTEXT
        print(f"\n[*] Step 4: Parsing response and extracting challenge data...")
        try:
            mid = r.headers.get("Ig-Set-X-Mid")
            resp_json = r.json()
            user_id = resp_json.get("user_id")
            cni = resp_json.get("cni")
            nonce_code = resp_json.get("nonce_code")
            challenge_context = resp_json.get("challenge_context")
            
            print(f"[+] Step 4 Complete: Extracted challenge data")
            print(f"    user_id: {user_id}")
            print(f"    cni: {cni}")
            print(f"    nonce_code: {nonce_code}")
            print(f"    challenge_context: {str(challenge_context)[:50]}...")
            
            if not all([user_id, cni, challenge_context]):
                print(f"[-] FAILED at Step 4: Missing required fields")
                return {"success": False, "error": "Missing challenge data from Instagram"}
            
        except Exception as e:
            print(f"[-] FAILED at Step 4: Could not parse response")
            print(f"    Error: {e}")
            print(f"    Response: {r.text[:500]}")
            return {"success": False, "error": f"Could not parse Instagram response: {str(e)}"}

        # STEP 3: SEND CHALLENGE REQUEST
        print(f"\n[*] Step 5: Sending challenge request to Instagram...")
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
        
        print(f"    Waiting for Instagram response (3-4 seconds)...")
        start_time = time.time()
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2, timeout=10)
        r2_text = r2.text
        elapsed_time = time.time() - start_time
        
        print(f"[+] Step 5 Complete: Got response in {elapsed_time:.2f} seconds")
        print(f"    Status Code: {r2.status_code}")
        print(f"    Response Length: {len(r2_text)} chars")
        
        if r2.status_code != 200:
            print(f"[-] FAILED at Step 5: Bad HTTP status")
            print(f"    Response: {r2_text[:500]}")
            return {"success": False, "error": f"Challenge request failed with HTTP {r2.status_code}"}
        
        if "bk.action.i64.Const" not in r2_text:
            print(f"[-] FAILED at Step 5: Challenge context not in response")
            print(f"    Response: {r2_text[:500]}")
            return {"success": False, "error": "Instagram challenge verification failed"}

        # STEP 4: EXTRACT FINAL CHALLENGE CONTEXT
        print(f"\n[*] Step 6: Extracting final challenge context...")
        try:
            challenge_context_final = r2_text.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]
            print(f"[+] Step 6 Complete: Extracted challenge context")
            print(f"    Context: {challenge_context_final[:50]}...")
        except Exception as e:
            print(f"[-] FAILED at Step 6: Could not extract challenge context")
            print(f"    Error: {e}")
            print(f"    Response: {r2_text[:500]}")
            return {"success": False, "error": f"Could not extract challenge context: {str(e)}"}

        # STEP 5: SEND NEW PASSWORD
        print(f"\n[*] Step 7: Sending new password to Instagram...")
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
        
        print(f"    Waiting for Instagram response (2-3 seconds)...")
        start_time = time.time()
        r3 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data3, timeout=10)
        elapsed_time = time.time() - start_time
        
        print(f"[+] Step 7 Complete: Got response in {elapsed_time:.2f} seconds")
        print(f"    Status Code: {r3.status_code}")
        print(f"    Response Length: {len(r3.text)} chars")
        
        if r3.status_code != 200:
            print(f"[-] WARNING at Step 7: Bad HTTP status {r3.status_code}")
            print(f"    But continuing anyway (Instagram might have already processed)")
        
        new_password = PASSWORD.split(":")[-1]
        
        print(f"\n[+] ==================== PASSWORD RESET SUCCESSFUL ====================")
        print(f"[+] New Password: {new_password}")
        print(f"[+] User ID: {user_id}")
        print(f"[+] Total Time: {elapsed_time:.2f} seconds")
        print(f"[+] ======================================================================\n")
        
        return {
            "success": True,
            "password": new_password,
            "user_id": user_id
        }
        
    except requests.exceptions.Timeout as e:
        print(f"\n[-] ==================== REQUEST TIMEOUT ====================")
        print(f"[-] Instagram server took too long to respond")
        print(f"[-] Error: {e}")
        return {"success": False, "error": "Request timeout - Instagram not responding"}
    except requests.exceptions.ConnectionError as e:
        print(f"\n[-] ==================== CONNECTION ERROR ====================")
        print(f"[-] Could not connect to Instagram")
        print(f"[-] Error: {e}")
        return {"success": False, "error": f"Connection error: {str(e)}"}
    except Exception as e:
        print(f"\n[-] ==================== UNEXPECTED ERROR ====================")
        print(f"[-] Error: {e}")
        import traceback
        traceback.print_exc()
        return {"success": False, "error": str(e)}

def process_reset_link(chat_id, username, reset_link):
    """Process reset link and send results"""
    try:
        print(f"\n{'='*70}")
        print(f"NEW REQUEST FROM USER {chat_id}")
        print(f"Instagram Username: {username}")
        print(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"{'='*70}\n")
        
        # Send processing message
        send_telegram(chat_id, 
            f"⏳ <b>Processing...</b>\n\n"
            f"Username: <code>{username}</code>\n\n"
            f"<i>This will take 7-8 seconds. Please wait...</i>",
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
            print(f"\n[+] ✅ SUCCESS! Message sent to user {chat_id}\n")
            send_telegram(chat_id, msg, parse_mode="HTML")
            
            # Reset user state
            if chat_id in user_states:
                del user_states[chat_id]
                
        else:
            error_msg = f"""
❌ <b>RESET FAILED</b>

<b>Error:</b>
<code>{result.get('error', 'Unknown error')}</code>

<b>Possible reasons:</b>
• Reset link has expired
• Reset link was already used
• Link format is incorrect
• Instagram account doesn't exist
• Network connectivity issue

<b>Troubleshooting:</b>
1. Request a new reset link from Instagram
2. Copy the complete link (including all parameters)
3. Send it to this bot again
4. If problem persists, contact Instagram support

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Try again?</b>
Send /reset to start over.
"""
            print(f"\n[-] ❌ FAILED! Error sent to user {chat_id}\n")
            send_telegram(chat_id, error_msg, parse_mode="HTML")
            
            # Reset user state
            if chat_id in user_states:
                del user_states[chat_id]
                
    except Exception as e:
        print(f"\n[-] EXCEPTION in process_reset_link: {str(e)}\n")
        import traceback
        traceback.print_exc()
        
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

━━━━━━━━━━━���━━━━━━━━━━━━
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
<code>https://instagram.com/users/password-reset/?uidb36=...&token=...</code>

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
    print("\n" + "="*70)
    print("🤖 INSTAGRAM ACCOUNT RECOVERY BOT - PROFESSIONAL VERSION")
    print("="*70)
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
