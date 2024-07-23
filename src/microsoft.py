import time

from src.util import *

# thanks dewycube for oauth2 code flow and covers1624 for device code flow
# https://gist.github.com/dewycube/223d4e9b3cddde932fbbb7cfcfb96759
# https://github.com/covers1624/DevLogin/blob/main/src/main/java/net/covers1624/devlogin/MicrosoftOAuth.java

CLIENT_ID = "00000000402B5328"
TENANT_ID = "170105bd-9573-4222-b09c-6f24c3b77cd8" # Original tenant ID included in DevLogin source code, TODO: change this

def oauth2_flow(session):
    # TODO: PyQt webview or something
    print(f"https://login.live.com/oauth20_authorize.srf?client_id={CLIENT_ID}&redirect_uri=https://login.live.com/oauth20_desktop.srf&response_type=code&scope=service::user.auth.xboxlive.com::MBI_SSL")
    code = input("Redirected URL: ").split("code=")[1].split("&")[0]

    r = session.post("https://login.live.com/oauth20_token.srf", data={
        "client_id": CLIENT_ID,
        "scope": "service::user.auth.xboxlive.com::MBI_SSL",
        "code": code,
        "redirect_uri": "https://login.live.com/oauth20_desktop.srf",
        "grant_type": "authorization_code"
    })

    return (r.json()["access_token"], r.json()["refresh_token"])

def device_code_flow(session):
    r = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/devicecode", data={
        "client_id": TENANT_ID,
        "scope": "XboxLive.signin offline_access"
    })

    user_code = r.json()["user_code"]
    device_code = r.json()["device_code"]
    verification_uri = r.json()["verification_uri"]
    expires_in = r.json()["expires_in"]
    interval = r.json()["interval"]

    print(f"{verification_uri} Code: {user_code} Expires in: {expires_in}s")

    while True:
        r = session.post("https://login.microsoftonline.com/consumers/oauth2/v2.0/token", data={
            "grant_type": "urn:ietf:params:oauth:grant-type:device_code",
            "client_id": TENANT_ID,
            "device_code": device_code
        })

        if r.status_code != 200:
            error = r.json()["error"]

            if error == "authorization_pending":
                pass
            elif error == "slow_down":
                interval *= 2
            elif error == "authorization_declined":
                log("Authorization declined")
                return
            elif error == "expired_token":
                log("Token expired, try again!")
                return
            else:
                log("Unknown error")
                return
        else:
            return (r.json()["access_token"], r.json()["refresh_token"])

        time.sleep(interval)

def jwt_token(ms_token, session):
    r = session.post("https://user.auth.xboxlive.com/user/authenticate", json={
        "Properties": {
            "AuthMethod": "RPS",
            "SiteName": "user.auth.xboxlive.com",
            "RpsTicket": ms_token
        },
        "RelyingParty": "http://auth.xboxlive.com",
        "TokenType": "JWT"
    })

    xbl_token = r.json()["Token"]

    r = session.post("https://xsts.auth.xboxlive.com/xsts/authorize", json={
        "Properties": {
            "SandboxId": "RETAIL",
            "UserTokens": [xbl_token]
        },
        "RelyingParty": "rp://api.minecraftservices.com/",
        "TokenType": "JWT"
    })

    xsts_userhash = r.json()["DisplayClaims"]["xui"][0]["uhs"]
    xsts_token = r.json()["Token"]

    r = session.post("https://api.minecraftservices.com/authentication/login_with_xbox", json={
        "identityToken": f"XBL3.0 x={xsts_userhash};{xsts_token}"
    })

    minecraft_token = r.json()["access_token"]

    r = session.get("https://api.minecraftservices.com/minecraft/profile", headers={
        "Authorization": f"Bearer {minecraft_token}"
    })

    username = r.json()["name"]
    uuid = r.json()["id"]

    return (username, uuid, minecraft_token)

def refresh_token(ms_token_rf, session):
    r = session.post("https://login.live.com/oauth20_token.srf", data={
        "scope": "service::user.auth.xboxlive.com::MBI_SSL",
        "client_id": CLIENT_ID,
        "grant_type": "refresh_token",
        "refresh_token": ms_token_rf
    })

    return r.json()["access_token"]

if __name__ == "__main__":
    import requests
    session = requests.Session()

    ms_token, ms_token_rf = oauth2_flow(session)
    username, uuid, minecraft_token = jwt_token(ms_token, session)

    log(f"Username: {username}")
    log(f"UUID: {uuid}")
    log(f"Token: {minecraft_token}")
    log(f"Refresh Token: {ms_token_rf}")
