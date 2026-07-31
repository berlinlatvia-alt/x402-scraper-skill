import os
import urllib.request
import urllib.parse
import json

def send_telegram_alert(message: str, priority: str = "HIGH"):
    """
    Core Tier-4 Escalation Hook.
    Bypasses the 'Autonomy' penalty to alert the human executive of critical failures,
    infrastructure blockers, or manager demotions.
    """
    env_path = r"C:\Users\smmgo\Documents\Obsidian Vault\HF-Trading-Project\.env"
    env_vars = {}
    if os.path.exists(env_path):
        with open(env_path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#") and "=" in line:
                    k, v = line.split("=", 1)
                    env_vars[k.strip()] = v.strip()
                    
    bot_token = env_vars.get("TELEGRAM_BOT_TOKEN") or os.environ.get("TELEGRAM_BOT_TOKEN")
    chat_id = env_vars.get("TELEGRAM_CHAT_ID") or os.environ.get("TELEGRAM_CHAT_ID")
    
    if not bot_token or not chat_id:
        print("TELEGRAM ERROR: Missing token or chat ID in environment.")
        return False

    prefix = {
        "CRITICAL": "🚨 [CRITICAL INFRASTRUCTURE BLOCK]",
        "HIGH": "⚠️ [TIER-4 ESCALATION]",
        "MEDIUM": "ℹ️ [SWARM NOTIFICATION]"
    }.get(priority.upper(), "⚠️ [ALERT]")

    formatted_message = f"{prefix}\n\n{message}"
    
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    data = urllib.parse.urlencode({
        "chat_id": chat_id,
        "text": formatted_message,
        "parse_mode": "Markdown"
    }).encode("utf-8")
    
    try:
        req = urllib.request.Request(url, data=data)
        with urllib.request.urlopen(req, timeout=10) as resp:
            res = json.loads(resp.read().decode("utf-8"))
            if res.get("ok"):
                print("Telegram alert successfully dispatched to Tier-4 Executive.")
                return True
            else:
                print(f"Telegram API returned error: {res}")
                return False
    except Exception as e:
        print(f"Failed to send Telegram alert: {str(e)}")
        return False

# Monkey-patching global exception handler to automatically fire Telegram alerts for uncaught criticals
def install_global_exception_hook():
    import sys
    import traceback
    
    def exception_handler(exc_type, exc_value, exc_traceback):
        # Ignore keyboard interrupts
        if issubclass(exc_type, KeyboardInterrupt):
            sys.__excepthook__(exc_type, exc_value, exc_traceback)
            return
            
        error_msg = "".join(traceback.format_exception(exc_type, exc_value, exc_traceback))
        alert_body = f"*FATAL SWARM CRASH*\n\nType: `{exc_type.__name__}`\nValue: `{exc_value}`\n\nThe script crashed. Human intervention required."
        send_telegram_alert(alert_body, priority="CRITICAL")
        
        # Call the default handler to still print to stderr
        sys.__excepthook__(exc_type, exc_value, exc_traceback)

    sys.excepthook = exception_handler
