from flask import Flask, request, session, redirect, url_for, render_template_string
from datetime import datetime, timedelta
import bcrypt
import os

app = Flask(__name__)
app.secret_key = os.urandom(32)  # Starkes, zufälliges Secret Key, nie hardcoden!

# FIX 1: Passwörter mit bcrypt gehasht, niemals im Klartext!
def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()

USERS = {
    "admin": hash_password("password123"),  # → $2b$12$... (irreversibel)
    "alice": hash_password("letmein"),
    "bob":   hash_password("123456"),
}

#FIX 2 & 3: Brute-Force-Schutz durch Rate-Limiting & Account-Lockout
LOGIN_ATTEMPTS: dict[str, list] = {}
MAX_ATTEMPTS   = 5
LOCKOUT_MINUTES = 5

def is_locked_out(username: str) -> tuple[bool, int]:
    """Gibt zurück: (ist_gesperrt, verbleibende_Sekunden)"""
    now     = datetime.utcnow()
    window  = timedelta(minutes=LOCKOUT_MINUTES)
    recent  = [t for t in LOGIN_ATTEMPTS.get(username, []) if now - t < window]
    LOGIN_ATTEMPTS[username] = recent  # Alte Einträge bereinigen
    if len(recent) >= MAX_ATTEMPTS:
        oldest    = min(recent)
        remaining = int((oldest + window - now).total_seconds())
        return True, remaining
    return False, 0

def record_attempt(username: str):
    LOGIN_ATTEMPTS.setdefault(username, []).append(datetime.utcnow())

def clear_attempts(username: str):
    LOGIN_ATTEMPTS.pop(username, None)

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🔒 Secure Login</title>
    <style>
        body   { font-family: Arial; max-width: 420px; margin: 80px auto; padding: 20px; background: #f9f9f9; }
        h2     { color: #27ae60; }
        input  { display: block; width: 100%; margin: 8px 0; padding: 10px; font-size: 16px; box-sizing: border-box; border: 1px solid #ccc; }
        button { width: 100%; padding: 12px; background: #27ae60; color: white; border: none; font-size: 16px; cursor: pointer; margin-top: 8px; }
        .error  { color: #c0392b; font-weight: bold; }
        .locked { background: #f8d7da; padding: 12px; border-left: 5px solid #dc3545; margin-bottom: 15px; }
        .ok     { background: #d4edda; padding: 10px; border-left: 4px solid #28a745; margin-bottom: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <h2>🔒 Login (Secure App)</h2>
    <div class="ok">✅ bcrypt-Hashing · Account-Lockout · Sichere Fehlermeldungen</div>
    {% if locked %}
        <div class="locked">
            🔒 <strong>Konto temporär gesperrt.</strong><br>
            Zu viele Fehlversuche. Bitte warte <strong>{{ remaining }}</strong> Sekunden.
        </div>
    {% else %}
        {% if error %}<p class="error">⛔ {{ error }}</p>{% endif %}
        <form method="POST">
            <input name="username" placeholder="Benutzername" autocomplete="username">
            <input name="password" type="password" placeholder="Passwort" autocomplete="current-password">
            <button type="submit">Einloggen</button>
        </form>
    {% endif %}
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Dashboard – Secure</title>
<style>
body { font-family: Arial; max-width: 420px; margin: 80px auto; padding: 20px; background: #f9f9f9; }
.box { background: #d4edda; padding: 20px; border-left: 5px solid #28a745; border-radius: 4px; }
a { display: inline-block; margin-top: 15px; color: #27ae60; text-decoration: none; }
</style>
</head>
<body>
    <div class="box">
        <h2>✅ Eingeloggt als: <strong>{{ user }}</strong></h2>
        <p>Willkommen! Login war erfolgreich und sicher.</p>
    </div>
    <a href="/logout">← Ausloggen</a>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # Lockout-Check zuerst
        locked, remaining = is_locked_out(username)
        if locked:
            # HTTP 429 = "Too Many Requests" → klar erkennbar für Script & Browser
            return render_template_string(LOGIN_HTML, locked=True, remaining=remaining), 429

        hashed = USERS.get(username)

        # bcrypt-Vergleich: konstante Ausführungszeit → kein Timing-Angriff möglich
        if hashed and bcrypt.checkpw(password.encode(), hashed.encode()):
            clear_attempts(username)  # Zähler zurücksetzen nach erfolgreichem Login
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            record_attempt(username)  # Fehlversuch registrieren
            # Generische Fehlermeldung: Verrät nicht ob Username oder Passwort falsch
            error = "Benutzername oder Passwort falsch."

    return render_template_string(LOGIN_HTML, error=error, locked=False)

@app.route("/dashboard")
def dashboard():
    if "user" not in session:
        return redirect(url_for("login"))
    return render_template_string(DASHBOARD_HTML, user=session["user"])

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

if __name__ == "__main__":
    app.run(debug=False, port=5001)  # debug=False in Produktion