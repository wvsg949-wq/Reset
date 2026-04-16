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

chat_id = os.getenv("CHAT_ID")
bot_token = os.getenv("BOT_TOKEN")

if not bot_token or not chat_id:
    print("❌ Missing BOT_TOKEN or CHAT_ID")
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
		
		r = requests.get(url, headers=headers)
		
		try:
		    username = r.json()["user"]["username"]
		    return username
		except:
		    print("Failed:", r.text)
	except:pass	    
	    
	    
def reset_instagram_password(reset_link):
    try:
        
        ANDROID_ID, USER_AGENT, WATERFALL_ID, PASSWORD = generate_device_info()
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
        r = requests.post(url, headers=make_headers(user_agent=USER_AGENT), data=data)
        
        if "user_id" not in r.text:
            return {"success": False, "error": f"Error in reset request: {r.text}"}

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
        r2 = requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data2).text
        
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
        
        requests.post(url2, headers=make_headers(mid, USER_AGENT), data=data3)
        new_password = PASSWORD.split(":")[-1]
        
        
        return {
    "success": True,
    "password": new_password,
    "user_id": user_id
    }
        
                
    except Exception as e:
        return False

def banner():
	WDEH = render('{END}', colors=['red', 'white'], align='center')

def process_link(reset_link):
    result = reset_instagram_password(reset_link)
    if result.get("success"):
        user_id = result.get("user_id")
        new_password = result.get("password")
        username = id_user(user_id)
        msg = f'''𓄅 𝗦𝗔𝗧𝗔𝗡 𝗦𝗘𝗡𝗗 𝗔 𝗠𝗘𝗦𝗦𝗔𝗚𝗘

⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘

[+] 𝗨𝗦𝗘𝗥𝗡𝗔𝗠𝗘 : {username}
[+] 𝗣𝗔𝗦𝗦𝗪𝗢𝗥𝗗: {new_password}

⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘⫘

𝗕𝗬 : @xYourKing 𝗖𝗛 : @xPythonTool
'''
        print(msg)
        send_telegram(bot_token, chat_id, msg)
        print("\nDone ✅")
    else:
        print("[-] Failed to reset password")
        send_telegram(bot_token, chat_id, "❌ Failed to reset password. Invalid link or already used.")

def get_updates(offset=0):
    """Get messages from Telegram"""
    url = f"https://api.telegram.org/bot{bot_token}/getUpdates"
    try:
        r = requests.post(url, json={"offset": offset, "timeout": 30}, timeout=35)
        return r.json()
    except:
        return {"ok": False, "result": []}

def main():
    banner()
    print("\n[+] Bot started. Listening for reset links...\n")
    
    offset = 0
    
    while True:
        try:
            response = get_updates(offset)
            
            if response.get("ok"):
                for update in response.get("result", []):
                    offset = update.get("update_id") + 1
                    message = update.get("message", {})
                    text = message.get("text", "")
                    msg_chat_id = message.get("chat", {}).get("id")
                    
                    if text and msg_chat_id == int(chat_id):
                        if "uidb36=" in text and "token=" in text:
                            print(f"[+] Processing link from {msg_chat_id}")
                            send_telegram(bot_token, chat_id, "⏳ Processing your reset link...")
                            process_link(text)
                        else:
                            send_telegram(bot_token, chat_id, "Send a valid Instagram reset link")
            
            time.sleep(1)
        except KeyboardInterrupt:
            print("\n[!] Bot stopped")
            break
        except Exception as e:
            print(f"[-] Error: {e}")
            time.sleep(5)

if __name__ == "__main__":
    main()
