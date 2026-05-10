# -*- coding: utf-8 -*-
"""
adhahi.dz – Auto-Register Bot
==========================================
1. Polls the adhahi.dz API every 2 seconds.
2. The moment a target wilaya becomes available:
   → Opens Chrome automatically.
   → Fills in personal information.
   → Selects wilaya + commune.
   → Pauses for CAPTCHA (must be solved manually).
   → Sends a Telegram alert.

REQUIREMENTS:
  pip install -r requirements.txt

HOW TO RUN:
  1. Fill in your personal information below.
  2. python auto_register.py
"""

import time
import json
import sys
import urllib.request
import urllib.error
from datetime import datetime

sys.stdout.reconfigure(encoding="utf-8", line_buffering=True)

# ══════════════════════════════════════════════════════════════════
#  ✏️  FILL IN YOUR PERSONAL INFORMATION BELOW
# ══════════════════════════════════════════════════════════════════

PERSONAL_INFO = {
    "nin":      "109970899031320005",                     # رقم التعريف الوطني – 18 digits
    "cni":      "102903385",                     # رقم بطاقة الهوية  – 9 digits
    "phone":    "0654992342",                     # رقم الهاتف (starts with 0, e.g., 05...)
    "email":    "bahaacostaluca@gmail.com",                     # البريد الإلكتروني (optional, leave "" to skip)
    "password": "Bahae2019@",                     # كلمة المرور
    "wilaya":   "المدية",                 # اسم الولاية بالعربية
    "commune":  "بن شكاو",                 # اسم البلدية بالعربية
    "payment":  "tpe",                 # "cash"  |  "tpe"  |  "online"
}

# ══════════════════════════════════════════════════════════════════
#  ✏️  TELEGRAM (optional – keeps you notified on your phone)
# ══════════════════════════════════════════════════════════════════

BOT_TOKEN        = ""                   # e.g., "123456789:ABCdefGHIjklMNOpqrs..."
PERSONAL_CHAT_ID = ""                   # e.g., "987654321"

# ══════════════════════════════════════════════════════════════════
#  Config
# ══════════════════════════════════════════════════════════════════

TARGET_WILAYA_CODE = "26"          # e.g., 19 for Sétif
CHECK_INTERVAL     = 2             # seconds between API polls
API_URL            = "https://adhahi.dz/api/v1/public/wilaya-quotas"
REGISTER_URL       = "https://adhahi.dz/register"
TELEGRAM_API       = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

REQUEST_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/147.0.0.0 Safari/537.36"
    ),
    "Accept": "application/json",
}


# ── Helpers ───────────────────────────────────────────────────────

def now() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def send_telegram(text: str):
    if not BOT_TOKEN or not PERSONAL_CHAT_ID:
        return
    try:
        payload = json.dumps({
            "chat_id": PERSONAL_CHAT_ID,
            "text": text,
            "parse_mode": "HTML",
        }).encode("utf-8")
        req = urllib.request.Request(
            TELEGRAM_API, data=payload,
            headers={"Content-Type": "application/json"}, method="POST",
        )
        urllib.request.urlopen(req, timeout=10)
    except Exception as e:
        print(f"  [Telegram] {e}")


def fetch_quotas() -> list:
    req = urllib.request.Request(API_URL, headers=REQUEST_HEADERS)
    with urllib.request.urlopen(req, timeout=15) as resp:
        return json.loads(resp.read())


def is_target_available(data: list) -> bool:
    target = TARGET_WILAYA_CODE.zfill(2)
    for entry in data:
        if str(entry.get("wilayaCode", "")).zfill(2) == target:
            return entry.get("available", False)
    return False


# ── Browser automation ────────────────────────────────────────────

def fill_and_submit():
    """Open Chrome and fill the registration form automatically."""
    try:
        from selenium import webdriver
        from selenium.webdriver.common.by import By
        from selenium.webdriver.common.keys import Keys
        from selenium.webdriver.support.ui import WebDriverWait
        from selenium.webdriver.support import expected_conditions as EC
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
    except ImportError:
        print("\n❌ Missing dependency. Run:  pip install -r requirements.txt\n")
        sys.exit(1)

    p = PERSONAL_INFO

    print(f"[{now()}] 🌐 Opening Chrome …")
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options,
    )
    wait = WebDriverWait(driver, 30)

    try:
        driver.get(REGISTER_URL)
        print(f"[{now()}] ✓ Page loaded: {REGISTER_URL}")

        def fill(selector, value):
            el = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, selector)))
            el.clear()
            el.send_keys(value)

        def click(selector):
            el = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
            driver.execute_script("arguments[0].scrollIntoView(true);", el)
            el.click()

        # ── Personal fields ───────────────────────────────────────
        fill("#reg-nin",              p["nin"])
        print(f"[{now()}] ✓ NIN filled")

        fill("#reg-cni",              p["cni"])
        print(f"[{now()}] ✓ CNI filled")

        fill("#reg-phone",            p["phone"])
        print(f"[{now()}] ✓ Phone filled")

        if p["email"]:
            fill("#reg-email",        p["email"])
            print(f"[{now()}] ✓ Email filled")

        fill("#reg-password",         p["password"])
        fill("#reg-confirm-password", p["password"])
        print(f"[{now()}] ✓ Password filled")

        # ── Wilaya (searchable combobox) ──────────────────────────
        wilaya_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#reg-wilaya")))
        wilaya_input.click()
        time.sleep(0.5)
        wilaya_input.send_keys(p["wilaya"])
        time.sleep(1.5)   # wait for dropdown to populate
        # Press Enter or click the first option
        wilaya_input.send_keys(Keys.ARROW_DOWN)
        wilaya_input.send_keys(Keys.RETURN)
        print(f"[{now()}] ✓ Wilaya selected: {p['wilaya']}")

        # ── Commune (appears after wilaya selection) ──────────────
        time.sleep(2)     # wait for commune list to load
        commune_input = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "#reg-commune")))
        commune_input.click()
        time.sleep(0.5)
        commune_input.send_keys(p["commune"])
        time.sleep(1.5)
        commune_input.send_keys(Keys.ARROW_DOWN)
        commune_input.send_keys(Keys.RETURN)
        print(f"[{now()}] ✓ Commune selected: {p['commune']}")

        # ── Payment method ────────────────────────────────────────
        time.sleep(1)
        payment_map = {"cash": 0, "tpe": 1, "online": 2}
        idx = payment_map.get(p["payment"].lower(), 0)
        radios = driver.find_elements(By.CSS_SELECTOR, "[role='radio']")
        if radios and idx < len(radios):
            driver.execute_script("arguments[0].click();", radios[idx])
            print(f"[{now()}] ✓ Payment: {p['payment']}")

        # ── Agreement checkbox ─────────────────────────────────────
        time.sleep(0.5)
        click("#reg-law-1807-checkbox")
        print(f"[{now()}] ✓ Agreement checked")

        # ── CAPTCHA — manual step ─────────────────────────────────
        print(f"\n{'─'*55}")
        print("  🔒 CAPTCHA required — solve it in the browser window")
        print("     Then click SUBMIT yourself (or press Enter here)")
        print(f"{'─'*55}")
        send_telegram(
            "🔒 <b>CAPTCHA needed!</b>\n"
            "Open the browser and solve the CAPTCHA to complete registration.\n"
            f"⏰ {now()}"
        )
        input("  → Press Enter after solving the CAPTCHA and submitting … ")

        # ── OTP step ──────────────────────────────────────────────
        print(f"\n{'─'*55}")
        print("  📱 You should receive an SMS OTP — enter it in the browser")
        print(f"{'─'*55}")
        send_telegram(
            "📱 <b>OTP sent to your phone!</b>\n"
            "Enter the 6-digit code in the browser to complete registration.\n"
            f"⏰ {now()}"
        )
        input("  → Press Enter after entering the OTP … ")

        print(f"\n[{now()}] ✅ Registration complete! Check adhahi.dz for confirmation.")
        send_telegram(
            "✅ <b>Registration submitted!</b>\n"
            "Check adhahi.dz to confirm your booking.\n"
            f"⏰ {now()}"
        )

    except Exception as e:
        print(f"[{now()}] ❌ Browser error: {e}")
        send_telegram(f"❌ Auto-fill error: {e}")
    finally:
        input("\n  → Press Enter to close the browser … ")
        driver.quit()


# ── Main polling loop ─────────────────────────────────────────────

def main():
    print("=" * 55)
    print("  adhahi.dz – Auto-Register Bot")
    print(f"  Waiting for Wilaya {TARGET_WILAYA_CODE} to open …")
    print(f"  Polling every {CHECK_INTERVAL}s  –  Press Ctrl+C to stop")
    print("=" * 55)

    send_telegram(
        "🤖 <b>Auto-Register Bot started</b>\n"
        f"Watching Wilaya {TARGET_WILAYA_CODE} — will auto-fill the form the moment it opens!\n"
        f"⏰ {now()}"
    )

    attempt = 0
    while True:
        attempt += 1
        ts = now()
        try:
            data = fetch_quotas()
            if is_target_available(data):
                print(f"\n{'!'*55}")
                print(f"  🎉 WILAYA {TARGET_WILAYA_CODE} IS OPEN! Launching browser …  [{ts}]")
                print(f"{'!'*55}\n")
                send_telegram(
                    f"🚨 <b>WILAYA {TARGET_WILAYA_CODE} IS AVAILABLE!</b>\n"
                    "Opening Chrome and filling the form NOW!\n"
                    f"⏰ {ts}"
                )
                fill_and_submit()
                break   # done
            else:
                print(f"[{ts}] #{attempt:04d} – Wilaya not available yet …")
        except urllib.error.HTTPError as e:
            print(f"[{ts}] #{attempt:04d} – HTTP {e.code}: {e.reason}")
            # Optional: Add sleep here if you want to back off after an error
        except urllib.error.URLError as e:
            print(f"[{ts}] #{attempt:04d} – Network error: {e.reason}")
        except Exception as e:
            print(f"[{ts}] #{attempt:04d} – Error: {e}")

        time.sleep(CHECK_INTERVAL)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n[{now()}] Stopped by user.")
        sys.exit(0)
