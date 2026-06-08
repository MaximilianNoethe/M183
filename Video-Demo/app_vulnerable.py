from flask import Flask, request, session, redirect, url_for, render_template_string

app = Flask(__name__)
app.secret_key = "supersecret123"  # Schwaches Secret Key (hardcoded!)

# SCHWACHSTELLE 1: Plaintext-Storage, Passwörter niemals im Klartext speichern!
USERS = {
    "admin": "password123",
    "alice": "letmein",
    "bob":   "123456",
}

LOGIN_HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>🔓 Vulnerable Login</title>
    <style>
        body { font-family: Arial; max-width: 420px; margin: 80px auto; padding: 20px; background: #f9f9f9; }
        h2 { color: #c0392b; }
        input { display: block; width: 100%; margin: 8px 0; padding: 10px; font-size: 16px; box-sizing: border-box; border: 1px solid #ccc; }
        button { width: 100%; padding: 12px; background: #e74c3c; color: white; border: none; font-size: 16px; cursor: pointer; margin-top: 8px; }
        .error  { color: #c0392b; font-weight: bold; }
        .warn   { background: #fff3cd; padding: 10px; border-left: 4px solid #ffc107; margin-bottom: 15px; font-size: 14px; }
    </style>
</head>
<body>
    <h2>🔓 Login (Vulnerable App)</h2>
    <div class="warn">⚠️ Demo-App: Absichtlich unsicher – nur für Bildungszwecke!</div>
    {% if error %}<p class="error">⛔ {{ error }}</p>{% endif %}
    <form method="POST">
        <input name="username" placeholder="Benutzername" value="{{ username or '' }}" autocomplete="off">
        <input name="password" type="password" placeholder="Passwort" autocomplete="off">
        <button type="submit">Einloggen</button>
    </form>
</body>
</html>
"""

DASHBOARD_HTML = """
<!DOCTYPE html>
<html>
<head><title>Dashboard – Vulnerable</title>
<style>
body { font-family: Arial; max-width: 420px; margin: 80px auto; padding: 20px; background: #f9f9f9; }
.box { background: #d4edda; padding: 20px; border-left: 5px solid #28a745; border-radius: 4px; }
a { display: inline-block; margin-top: 15px; color: #e74c3c; text-decoration: none; }
</style>
</head>
<body>
    <div class="box">
        <h2>✅ Eingeloggt als: <strong>{{ user }}</strong></h2>
        <p>Willkommen im gesicherten Bereich!<br>
        <small>(Diese Seite wäre in einer echten App hinter dem Login geschützt.)</small></p>
    </div>
    <a href="/logout">← Ausloggen</a>
</body>
</html>
"""

@app.route("/", methods=["GET", "POST"])
def login():
    error = None
    username = ""
    if request.method == "POST":
        username = request.form.get("username", "")
        password = request.form.get("password", "")

        # SCHWACHSTELLE 2: Kein Rate Limiting -> unbegrenzte Login Versuche möglich
        # SCHWACHSTELLE 3: Kein Account-Lockout -> Brute Force trivial möglich
        # Direkter Klartext-Vergleich
        if USERS.get(username) == password:
            session["user"] = username
            return redirect(url_for("dashboard"))
        else:
            error = "Falsches Passwort."  # Verrät, dass der Username korrekt ist!

    return render_template_string(LOGIN_HTML, error=error, username=username)

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
    app.run(debug=True, port=5000)  # debug=True niemals in Produktion!