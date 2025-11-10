# ?? BlankTB Portal — API Reference (v1)

**Backend Base URL:**  
`http://localhost:8000/api/` (LAN only)  
**Production URL:**  
`https://gba.blanktb.net/api/`

**Authorization:**  
All protected routes use `Bearer <JWT>` authentication.  
Public routes (login, register, about, privacy) require no token.

---

## ?? Overview

The **BlankTB Portal API** powers all frontend communication between the web interface and backend logic.  
It manages secure authentication, token redemptions, receipts, user dashboards, admin/reps panels, and contact systems.

The API is fully asynchronous (FastAPI + MongoDB Motor driver) and follows REST standards.

---

# ?? AUTHENTICATION ROUTES

### `POST /auth/login`
Authenticate existing user credentials.

**Body:**
```json
{
  "username": "exampleUser",
  "password": "Secret123!"
}

Response (200):

{
  "status": "ok",
  "token": "<JWT_TOKEN>",
  "expires_in": 86400
}

Response (403 - invalid):

{
  "status": "error",
  "message": "Invalid username or password."
}

    Notes:

        reCAPTCHA enforced after 3 failed attempts.

        One-device session policy enforced (previous logins are auto-expired).

POST /auth/token/redeem

Redeem a Portal Access Token for new or reactivated accounts.

Body:

{
  "token": "PORTAL-XYZ-123",
  "username": "newUser",
  "password": "SecretPass!",
  "email": "user@example.com",
  "type": "new"
}

Response (201):

{
  "status": "ok",
  "message": "Account created and access activated for 30 days."
}

POST /auth/logout

Log out the current session.

Headers:
Authorization: Bearer <JWT>

Response:

{"status": "ok", "message": "Logged out successfully."}

?? USER ROUTES
GET /users/me

Fetch current user profile.

Headers:
Authorization: Bearer <JWT>

Response:

{
  "username": "exampleUser",
  "email": "user@example.com",
  "access_expires": "2025-12-01T00:00:00Z",
  "tokens_used": 2,
  "status": "active",
  "notifications": 3
}

POST /users/update

Update user email, password, or username.

Body:

{
  "email": "new@example.com",
  "password": "NewPassword123"
}

Response:

{"status": "ok", "message": "Profile updated successfully."}

GET /users/notifications

Retrieve notifications sent to the user.

Response:

[
  {
    "title": "Security Alert",
    "message": "Another login detected. Prior session ended.",
    "date": "2025-11-07T22:00:00Z"
  }
]

??? TOKEN ROUTES
GET /tokens/active

List all active tokens and expiration dates.

Response:

[
  {"token_id": "TKN-001", "days": 30, "expires": "2025-12-01T00:00:00Z"}
]

POST /tokens/redeem

Redeem an additional token to extend access duration.

Body:

{"token": "PORTAL-NEW-456"}

Response:

{"status": "ok", "message": "Access extended by 30 days."}

?? RECEIPT ROUTES
GET /receipts/my

Get all receipts bound to the logged-in account.

Response:

[
  {
    "receipt_id": "RCPT-8921",
    "token": "PORTAL-NEW-456",
    "price": "$5.00",
    "issued_by": "RepName",
    "date": "2025-11-01T00:00:00Z"
  }
]

POST /reps/receipts/create

(Rep-Only) Issue a new receipt and email the token to a customer.

Body:

{
  "email": "user@example.com",
  "token_id": "PORTAL-NEW-456",
  "price": "$5.00"
}

Response:

{"status": "ok", "message": "Receipt sent to user@example.com."}

????? ADMIN ROUTES
POST /admin/tokens/create

Generate a new token with defined duration and price.

Body:

{"days": 30, "price": "$5.00"}

Response:

{
  "status": "ok",
  "token": "PORTAL-NEW-456",
  "days": 30,
  "price": "$5.00"
}

GET /admin/users

List all users with their account states.

Response:

[
  {
    "username": "exampleUser",
    "email": "user@example.com",
    "access_expires": "2025-12-01T00:00:00Z",
    "locked": false,
    "ip_last": "192.168.50.42"
  }
]

POST /admin/notify

Send an alert message directly to a user.

Body:

{
  "user_id": "65f9bde8",
  "title": "Reminder",
  "message": "Your access expires in 3 days!"
}

Response:

{"status": "ok", "message": "Notification delivered."}

POST /admin/flag

Mark a user for review or potential account sharing.

Body:

{
  "user_id": "65f9bde8",
  "reason": "Multiple IP logins within 5 minutes."
}

Response:

{"status": "ok", "message": "User flagged and supervision initiated."}

?? HELP & CONTACT ROUTES
POST /help/login

Submit help request from login page.

Body:

{
  "email": "user@example.com",
  "category": "Login Problem",
  "details": "My account says insufficient funds but I have a receipt."
}

Response:

{"status": "ok", "message": "Support ticket created. An admin will contact you shortly."}

POST /help/dashboard

Submit help request from user dashboard (for logged-in users).

Headers:
Authorization: Bearer <JWT>

Body:

{
  "category": "Token Issue",
  "details": "Token applied but time not extended."
}

Response:

{"status": "ok", "message": "Help request sent to admin."}

?? PUBLIC ROUTES
GET /public/about

Returns info for the About page.

Response:

{
  "title": "About BlankTB Portal",
  "description": "A private access platform for the BlankTB community.",
  "proprietors": ["Blank The Deer", "BlameKitts"]
}

GET /public/policies

Returns Privacy Policy and Terms of Service content.

Response:

{
  "privacy": "We do not collect personal data except for login credentials and account tokens...",
  "terms": "By using BlankTB Portal you agree that all access tokens are non-refundable..."
}

?? DEBUG ROUTES
GET /debug/db

Check MongoDB connection.

Response:

{"status": "ok", "collections": ["users", "tokens", "receipts"]}

GET /debug/ui

HTML diagnostics page for backend health.

Shows:

    MongoDB connection status

    System uptime

    CPU & memory usage

    FastAPI environment

?? Authentication Flow Diagram

Login ? [JWT Issued] ? Dashboard Access
 ?                     ?
Token Redeem ? [Access Extended] 
 ?
Receipt Linked ? [Visible in User Profile]
 ?
Admin/Rep Supervision ? Notifications Triggered

?? Status Codes
Code	Meaning
200	Successful operation
201	Created (new resource)
400	Invalid request
401	Unauthorized
403	Forbidden / reCAPTCHA required
404	Resource not found
409	Conflict (e.g., token already used)
500	Internal server error
?? Maintainers
Name	Role
Blank The Deer ??	Lead Developer / Backend Architect
BlameKitts ??	Co-Owner / Systems Integration
BlankTB Reps	Authorized Token Issuers / Support Contacts
?? License

© BlankTB — All Rights Reserved.
All code and assets under this backend are proprietary. Redistribution, sale, or modification without explicit written permission from BlankTB is prohibited.