# Adhahi.dz Auto-Register Bot 🇩🇿🐑

This script automates the process of booking a sheep on the Algerian platform [adhahi.dz](https://adhahi.dz/). Since quotas open randomly and fill up in seconds, this bot polls the API continuously and automatically fills out your registration form the moment your Wilaya opens.

## ⚠️ Important limitations

- **Geo-Blocking:** The `adhahi.dz` API blocks requests from outside Algeria. You **must** run this script on a local PC connected to an Algerian network, or on a VPS located inside Algeria. Cloud providers like GitHub Actions, Heroku, or Railway will fail with a Timeout / 403 Forbidden error.
- **Manual CAPTCHA & OTP:** The script will open Chrome and fill everything (NIN, CNI, phone, wilaya, commune), but it **will stop and wait for you** to solve the image CAPTCHA and input the SMS OTP. You will receive a Telegram notification when manual intervention is needed.

## 🚀 Setup

1. **Install dependencies:**  
   You need Python installed. Then run:
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure the script:**  
   Open `auto_register.py` in any text editor and fill in the `PERSONAL_INFO` dictionary at the top of the file:
   - Your `nin` (18 digits)
   - Your `cni` (9 digits)
   - Phone number, Password, Wilaya, and Commune
   - Which wilaya code to watch (`TARGET_WILAYA_CODE`, e.g., `"19"` for Sétif)

3. **(Optional) Telegram Setup:**  
   If you want a ping on your phone when your PC detects the wilaya opening:
   - Create a bot via `@BotFather` on Telegram.
   - Message `@userinfobot` to get your personal `CHAT_ID`.
   - Put them in the `BOT_TOKEN` and `PERSONAL_CHAT_ID` variables in the script.

## ▶️ Usage

Simply run the script in your terminal:

```bash
python auto_register.py
```

Leave your PC on. It will check every 2 seconds. When it detects an opening, Chrome will pop up, fill your data instantly, and wait for you to solve the CAPTCHA.

## Disclaimer

This is an unofficial script created to assist users with the fast-paced registration. Use it responsibly and at your own risk. Do NOT lower the poll interval to less than 1-2 seconds, or your IP may get temporarily blocked.
