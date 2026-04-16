import os
import random
from random import choice
from threading import Thread, Lock 
import requests
from user_agent import generate_user_agent
from hashlib import md5
from bs4 import BeautifulSoup
import base64
import secrets
from hashlib import md5
try:
    import requests
    import pyfiglet
    from rich.console import Console
    from cfonts import render, say
except ImportError:
    os.system("pip install requests telethon pyfiglet rich cfonts")

    
import time
b = random.randint(5,208)
bo = f'\x1b[38;5;{b}m'
ED='\x1b[38;5;208m'
BLUE = '\033[94m'
Z = '\033[1;31m' 
YELLOW = '\033[1;33m' 
import requests, random, string, uuid
from datetime import datetime
import base64
import json
from dotenv import load_dotenv
import sys

load_dotenv()

J = '\033[2;36m'
N = '\033[1;37m'

bot_token = os.getenv("BOT_TOKEN")
user_states = {}

if not bot_token:
    print("❌ Missing BOT_TOKEN")
    sys.exit(1)

def send_telegram(bot_token, chat_id, text):
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    try:
        r = requests.post(url, data=payload, timeout=10)
        return r.json()
    except Exception as e:
        print("[-] Telegram send error:", e)
        return None

def generate_device_info():
    ANDROID_ID = f"android-{''.join(random.choices(string.hexdigits.lower(), k=16))}"
    USER_AGENT = f"Instagram 394.0.0.46.81 Android ({random.choice(['28/9','29/10','30/11','31/12'])}; {random.choice(['240dpi','320dpi','480dpi'])}; {random.choice(['720x1280','1080x1920','1440x2560'])}; {random.choice(['samsung','xiaomi','huawei','oneplus','google'])}; {random.choice(['SM-G975F','Mi-9T','P30-Pro','ONEPLUS-A6003','Pixel-4'])}; intel; en_US; {random.randint(100000000,999999999)})"
    WATERFALL_ID = str(uuid.uuid4())
    timestamp = int(datetime.now().timestamp())
    nums = ''.join([str(random.randint(1, 100)) for _ in range(4)])
    PASSWORD = f'#PWD_INSTAGRAM:0:{timestamp}:Random@{nums}'
    return ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD

def make_headers(mid="", user_agent=""):
    return {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "X-Bloks-Version-Id": "e061cacfa956f06869fc2b678270bef1583d2480bf51f508321e64cfb5cc12bd",
        "X-Mid": mid,
        "User-Agent": user_agent,
        "Content-Length": "9481"
    }

def id_user(user_id):
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
            return "Unknown User"
    except:
        return "Unknown User"
    
    
def reset_instagram_password(reset_link):
    ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
    
    try:
        uidb36 = reset_link.split("uidb36=")[1].split("&token=")[0]
    except:
        return False
    
    try:
        token = reset_link.split("&token=")[1].split(":")[0]
    except:
        return False

    url = "https://i.instagram.com/api/v1/accounts/password_reset/"
    data = {
        "source": "one_click_login_email",
        "uidb36": uidb36,
        "device_id": ANDROID_ID,
        "token": token,
        "waterfall_id": WATERFALL_ID
    }
    
    try:
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data, timeout=15)
        print(f"[1] Response 1 status: {r.status_code}")
    except:
        return False
    
    if "user_id" not in r.text:
        print(f"[-] No user_id in response 1")
        return False

    try:
        mid = r.headers.get("Ig-Set-X-Mid")
        resp_json = r.json()
    except:
        print(f"[-] Could not parse response 1")
        return False
    
    user_id = resp_json.get("user_id")
    cni = resp_json.get("cni")
    nonce_code = resp_json.get("nonce_code")
    challenge_context = resp_json.get("challenge_context")
    
    if not user_id or not cni:
        print(f"[-] Missing user_id or cni")
        return False

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
    
    try:
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2, timeout=15)
        print(f"[2] Response 2 status: {r2.status_code}")
    except:
        print(f"[-] Request 2 failed")
        return False
    
    r2_text = r2.text
    
    if "bk.action.i64.Const" not in r2_text:
        print(f"[-] Challenge context not in response 2")
        return False

    try:
        challenge_context_final = r2_text.replace('\\', '').split(f'(bk.action.i64.Const, {cni}), "')[1].split('", (bk.action.bool.Const, false)))')[0]
    except:
        print(f"[-] Could not extract challenge context")
        return False

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
    
    try:
        r3 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data3, timeout=15)
        print(f"[3] Response 3 status: {r3.status_code}")
    except:
        print(f"[-] Request 3 failed")
        return False
    
    new_password = PASSWORD.split(":")[-1]
    
    return {
        "success": True,
        "password": new_password,
        "user_id": user_id
    }


def process_reset_link(chat_id, username, reset_link):
    """Process reset link in background"""
    send_telegram(bot_token, chat_id, f"⏳ <b>Processing for:</b> <code>{username}</code>\n\n<i>Please wait 7-8 seconds...</i>")
    
    result = reset_instagram_password(reset_link)
    
    if result and result.get("success"):
        user_id = result.get("user_id")
        new_password = result.get("password")
        username_verified = id_user(user_id)
        
        msg = f"""
✅ <b>SUCCESS!</b>

━━━━━━━━━━━━━━━━━━━━━━━━
<b>Account Details:</b>
━━━━━━━━━━━━━━━━━━━━━━━━

👤 <b>Username:</b> <code>{username_verified}</code>
🔐 <b>Password:</b> <code>{new_password}</code>
🆔 <b>User ID:</b> <code>{user_id}</code>

━━━━━━━━━━━━━━━━━━━━━━━━
"""
        send_telegram(bot_token, chat_id, msg)
        if chat_id in user_states:
            del user_states[chat_id]
    else:
        error_msg = """
❌ <b>RESET FAILED</b>

Possible reasons:
• Link expired or already used
• Invalid link format
• Account not found
• Network error

Send /reset to try again
"""
        send_telegram(bot_token, chat_id, error_msg)
        if chat_id in user_states:
            del user_states[chat_id]


def handle_message(chat_id, text):
    """Handle user messages"""
    
    if text.lower() == "/start":
        msg = """
👋 <b>Welcome!</b>

Send /reset to start account recovery
Send /help for more info
"""
        send_telegram(bot_token, chat_id, msg)
        return
    
    if text.lower() == "/reset":
        user_states[chat_id] = {"step": "username"}
        send_telegram(bot_token, chat_id, "📝 <b>Enter your Instagram username:</b>")
        return
    
    if text.lower() == "/help":
        msg = """
📚 <b>HOW TO USE:</b>

1. Send /reset
2. Enter your Instagram username
3. Send the password reset link
4. Get your new password!

⚠️ Only use on YOUR OWN accounts
"""
        send_telegram(bot_token, chat_id, msg)
        return
    
    if text.lower() == "/cancel":
        if chat_id in user_states:
            del user_states[chat_id]
        send_telegram(bot_token, chat_id, "❌ Cancelled")
        return
    
    if chat_id not in user_states:
        send_telegram(bot_token, chat_id, "Send /reset to start")
        return
    
    if user_states[chat_id]["step"] == "username":
        user_states[chat_id]["username"] = text
        user_states[chat_id]["step"] = "link"
        send_telegram(bot_token, chat_id, f"✅ Username: <code>{text}</code>\n\n📎 <b>Now send the reset link:</b>")
        return
    
    if user_states[chat_id]["step"] == "link":
        if "uidb36=" not in text or "token=" not in text:
            send_telegram(bot_token, chat_id, "❌ Invalid link format\n\nLink must contain uidb36= and token=\n\nTry again:")
            return
        
        username = user_states[chat_id]["username"]
        thread = Thread(target=process_reset_link, args=(chat_id, username, text))
        thread.daemon = True
        thread.start()


def get_updates(offset=0):
    """Get Telegram messages"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        r = requests.post(url, json={"offset": offset, "timeout": 30}, timeout=35)
        return r.json()
    except:
        return {"ok": False, "result": []}


def main():
    offset = 0
    print("\n" + "="*50)
    print("🤖 INSTAGRAM RESET BOT STARTED")
    print("="*50 + "\n")
    
    while True:
        try:
            response = get_updates(offset)
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update.get("update_id") + 1
                    message = update.get("message", {})
                    chat_id = message.get("chat", {}).get("id")
                    text = message.get("text", "")
                    
                    if chat_id and text:
                        print(f"[{datetime.now().strftime('%H:%M:%S')}] User {chat_id}: {text[:40]}")
                        handle_message(chat_id, text)
            
            time.sleep(0.1)
        except KeyboardInterrupt:
            print("\n[!] Bot stopped")
            break
        except Exception as e:
            print(f"[-] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
