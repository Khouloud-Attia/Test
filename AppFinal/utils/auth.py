# auth.py
import os
import msal  # pyright: ignore[reportMissingImports]
from utils.config import CLIENT_ID, AUTHORITY, SCOPES

def get_token_cache_path():
    """Retourne le chemin du cache token pour l'utilisateur courant"""
    appdata = os.getenv('APPDATA') or os.path.expanduser("~/.config")
    cache_dir = os.path.join(appdata, "MeetNotesAI")
    os.makedirs(cache_dir, exist_ok=True)
    return os.path.join(cache_dir, "token_cache.bin")

def get_access_token():
    TOKEN_PATH = get_token_cache_path()

    # 1️⃣ Charger le cache existant
    cache = msal.SerializableTokenCache()
    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "r") as f:
            cache.deserialize(f.read())

    # 2️⃣ Créer l'application MSAL avec ce cache
    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache
    )

    # 3️⃣ Essayer de récupérer le token silencieusement
    accounts = app.get_accounts()
    result = None
    if accounts:
        result = app.acquire_token_silent(SCOPES, account=accounts[0])

    # 4️⃣ Si pas de token valide → device flow interactif
    if not result:
        flow = app.initiate_device_flow(scopes=SCOPES)
        if "user_code" not in flow:
            raise ValueError("Impossible de créer le device flow : %s" % flow)
        print(flow["message"])
        result = app.acquire_token_by_device_flow(flow)

    # 5️⃣ Sauvegarder le cache pour cet utilisateur
    if cache.has_state_changed:
        with open(TOKEN_PATH, "w") as f:
            f.write(cache.serialize())

    # 6️⃣ Retourner le token
    if "access_token" in result:
        print("✅ Connexion réussie à Microsoft Graph API")
        return result["access_token"]
    else:
        raise Exception(f"❌ Erreur : {result.get('error')} - {result.get('error_description')}")
