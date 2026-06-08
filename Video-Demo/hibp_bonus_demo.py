import hashlib
import requests

def check_pwned(password: str) -> int:
    """
    Prüft via HaveIBeenPwned-API wie oft ein Passwort in Datenlecks vorkam.
    Verwendet k-Anonymity: Nur die ersten 5 Zeichen des SHA1-Hashes werden gesendet.
    Das eigentliche Passwort verlässt nie den lokalen Rechner.
    """
    sha1 = hashlib.sha1(password.encode()).hexdigest().upper()
    prefix = sha1[:5]
    suffix = sha1[5:]

    response = requests.get(
        f"https://api.pwnedpasswords.com/range/{prefix}",
        headers={"User-Agent": "OWASP-Demo-Educational"}
    )

    for line in response.text.splitlines():
        hash_suffix, count = line.split(":")
        if hash_suffix == suffix:
            return int(count)
    return 0

# Demo-Passwörter (dieselben wie in der vulnerable App)
DEMO_PASSWORDS = [
    "password123",   # Admin-Passwort aus der Demo
    "letmein",       # Alice's Passwort
    "123456",        # Bob's Passwort
    "S3cur3!xK9#mP", # Beispiel: Starkes Passwort
]

print("=" * 55)
print("🔍 Have I Been Pwned – Passwort-Check")
print("   (k-Anonymity: Das Passwort verlässt nie deinen PC!)")
print("=" * 55)

for pw in DEMO_PASSWORDS:
    try:
        count = check_pwned(pw)
        if count > 0:
            print(f"  ❌  '{pw}'")
            print(f"       → {count:,} Mal in echten Datenlecks gefunden!\n")
        else:
            print(f"  ✅  '{pw}'")
            print(f"       → Nicht in bekannten Datenlecks gefunden.\n")
    except Exception as e:
        print(f"  ⚠️  '{pw}' → Fehler: {e}\n")

print("=" * 55)
print("Fazit: Schwache Passwörter sind auf JEDER Brute-Force-")
print("Wordlist der Welt – z.B. RockYou2021 (8.4 Mrd Einträge).")
print("=" * 55)