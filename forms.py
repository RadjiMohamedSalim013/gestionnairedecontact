import secrets

# Générer une clé secrète aléatoire de 32 octets (adapté pour Flask/Django)
secret_key = secrets.token_hex(32)
print("Clé secrète générée :", secret_key)
