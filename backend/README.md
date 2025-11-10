# ?? BlankTB Portal — Backend (FastAPI + MongoDB)

**Domain:** [https://gba.blanktb.net](https://gba.blanktb.net)  
**License Holder:** BlankTB  
**Proprietors:** Blank The Deer & BlameKitts  
© BlankTB — All Rights Reserved.  

Unauthorized reproduction or distribution is strictly prohibited.

---

## ?? Overview

The **BlankTB Portal Backend** is the secure, logic-driven core of the **BlankTB Portal** — a private, token-based access platform that powers browser-based GBA emulation through a safe and controlled account system.

It handles:

- ?? Secure authentication (JWT + one-device session enforcement)
- ??? Token management (access duration, extensions, expirations)
- ?? Receipt linking for access validation
- ?? Rep and Admin tools for token creation and monitoring
- ?? REST APIs for the frontend dashboard
- ?? Email and notification delivery
- ?? Session supervision and login anomaly detection

It **does not** host ROMs, BIOS files, or copyrighted content.

---

## ?? Tech Stack

| Component | Description |
|------------|-------------|
| **FastAPI** | High-performance async backend framework |
| **MongoDB** | Database for users, tokens, receipts, and logs |
| **Motor** | Async MongoDB driver |
| **Uvicorn** | ASGI web server |
| **dotenv** | Secure environment variable handling |
| **ReCAPTCHA** | Bot protection on login/token endpoints |
| **systemd** | Persistent backend service manager |
| **UFW Firewall** | Restricts backend to LAN access only |

---

## ?? Project Structure

backend/
+-- .gitignore
+-- requirements.txt
+-- README.md
+-- .env.example
+-- app/
+-- main.py
+-- core/
¦ +-- config.py
¦ +-- security.py
¦ +-- emailer.py
¦ +-- recaptcha.py
+-- models/
¦ +-- user.py
¦ +-- token.py
¦ +-- receipt.py
¦ +-- help_ticket.py
¦ +-- notification.py
¦ +-- log.py
+-- routers/
¦ +-- auth.py
¦ +-- users.py
¦ +-- reps.py
¦ +-- admin.py
¦ +-- tokens.py
¦ +-- receipts.py
¦ +-- help.py
¦ +-- public.py
+-- services/
¦ +-- session_manager.py
¦ +-- supervision.py
¦ +-- fileops.py
+-- templates/
¦ +-- email_token.html
¦ +-- email_alert.html
+-- init.py


---

## ?? Core Functionalities

### ?? Authentication
- JWT-based login sessions  
- One active session per user  
- reCAPTCHA after 3 failed logins  
- Passwords hashed with bcrypt  
- Admin/Rep role validation  

### ??? Token & Access
- Tokens define access duration (e.g., 30 days)  
- Tokens extend access when redeemed  
- Reps issue tokens via receipts  
- Admins manage available token types  

### ?? Receipts
- Reps generate receipts that link tokens to users  
- Receipts store transaction details for auditing  
- Admins can view all; users can view personal ones  

### ??? Supervision
- Detects new IPs, concurrent logins  
- Locks or flags accounts on anomaly  
- Alerts admins in real-time  

### ?? Help System
- Users submit support tickets  
- Admins review and reply in portal  
- Discord webhook notifications for urgent help  

---

## ?? API Overview

| Type | Endpoint | Description |
|------|-----------|-------------|
| `POST` | `/api/auth/login` | Log in user |
| `POST` | `/api/auth/token/redeem` | Redeem new token |
| `POST` | `/api/auth/logout` | Log out current session |
| `GET` | `/api/users/me` | View user profile |
| `POST` | `/api/users/update` | Update email/password |
| `GET` | `/api/tokens/active` | List current access tokens |
| `GET` | `/api/receipts/my` | View receipts |
| `POST` | `/api/reps/receipts/create` | Rep issues token/receipt |
| `POST` | `/api/admin/tokens/create` | Admin creates new token type |
| `GET` | `/api/admin/users` | Admin user list |
| `POST` | `/api/admin/notify` | Admin sends user alert |
| `POST` | `/api/help/login` | Help form (login screen) |
| `GET` | `/api/public/about` | About page data |
| `GET` | `/api/debug/db` | Check MongoDB connection |
| `GET` | `/api/debug/ui` | HTML diagnostics dashboard |

?? Full endpoint documentation: [`API_REFERENCE.md`](./API_REFERENCE.md)

---

## ?? Environment Setup

### 1?? Create `.env` File

Example configuration:
```bash
MONGODB_URI=mongodb://Portal:Portalemu12@localhost:27017/blanktb_portal?authSource=blanktb_portal
SECRET_KEY=<super_secret_string>
RECAPTCHA_SECRET=<google_recaptcha_secret>
EMAIL_HOST=smtp.mailserver.com
EMAIL_USER=bot@blanktb.net
EMAIL_PASS=<password_here>
DISCORD_WEBHOOK=https://discord.com/api/webhooks/EXAMPLE
ADMIN_EMAIL=admin@blanktb.net

?? Testing the Backend
Run Locally:

uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

Check Health:

curl http://127.0.0.1:8000/api/debug/db
curl http://127.0.0.1:8000/api/debug/ui

Open API Docs:

    Swagger UI

ReDoc UI
? Run as Systemd Service

File: /etc/systemd/system/blanktb-backend.service

[Unit]
Description=BlankTB Portal Backend (FastAPI)
After=network.target

[Service]
User=blankthedeer
WorkingDirectory=/home/blankthedeer/gba/backend
ExecStart=/home/blankthedeer/gba/backend/.venv/bin/uvicorn app.main:app --host 0.0.0.0 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target

Commands:

sudo systemctl daemon-reload
sudo systemctl enable blanktb-backend
sudo systemctl start blanktb-backend
sudo systemctl status blanktb-backend
sudo journalctl -u blanktb-backend -f

?? Dependencies

Install required packages:

pip install -r requirements.txt

Example requirements.txt

fastapi
uvicorn
motor
pymongo
python-dotenv
email-validator
bcrypt
python-multipart
httpx
psutil

????? Admin Access

Admins are created manually in MongoDB.
Once created, admins can:

    Manage users

    Create tokens

    Issue receipts

    Monitor logs and supervision flags

?? Security

    All passwords hashed via bcrypt

    JWTs expire and auto-rotate

    MongoDB restricted to LAN only

    Firewall (ufw) blocks external 27017

    reCAPTCHA on login/token endpoints

    Single-session enforcement

?? Credits

Developed by: Blank The Deer ??
Systems Architect: BlameKitts ??
Project: BlankTB Portal

Support Server:
Discord Support

Community Server:
Discord Community
?? License

© BlankTB
— All Rights Reserved.
All source code, branding, and content belong to Blank The Deer & BlameKitts.
Redistribution, resale, or modification without explicit permission is prohibited.