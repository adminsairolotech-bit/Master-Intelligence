import requests
import json
import time

def check_ms_account(email):
    url = "https://login.microsoftonline.com/common/GetCredentialType"
    payload = {
        "username": email,
        "isEnterprise": False,
        "checkPhones": True,
        "isOtherIdpSupported": True,
        "isRemoteConnectSupported": False,
        "isFidoSupported": True,
        "isGlobalIdp": True,
        "isMicrosoftAccount": True,
    }
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0"
    }
    
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200:
            data = response.json()
            # If IfExistsResult is 0, the account exists. 
            # 5 means not found, 10 means locked/disabled.
            res = data.get("IfExistsResult")
            if res == 0:
                return "Active"
            elif res == 5:
                return "Not Found"
            elif res == 10:
                return "Locked/Disabled"
            else:
                return f"Result {res}"
        else:
            return f"Error {response.status_code}"
    except Exception as e:
        return f"Error: {str(e)}"

accounts = [
    "nycossferdulay@outlook.com", "veveccacopriv@outlook.com", "beiringbickumq@outlook.com",
    "razaigawliy@outlook.com", "prescillaspiottot@outlook.com", "tobeikamiraveti@outlook.com",
    "trussogeuidaf@outlook.com", "biulatorviky@outlook.com", "tanykiayijieg@outlook.com",
    "nimangorbass@outlook.com", "manafyciganekb@outlook.com", "meixiadayellc@outlook.com",
    "risolecilliet@outlook.com", "zijahumarahm@outlook.com", "breznykeolkerv@outlook.com",
    "doulykulaya95@outlook.com", "lobleantuazzf@outlook.com", "dezelanchaloeil@outlook.com",
    "tarlonpatikk@outlook.com", "deoudeskahiapoh@outlook.com"
]

print("Checking accounts...")
active = []
for email in accounts:
    status = check_ms_account(email)
    print(f"{email}: {status}")
    if status == "Active":
        active.append(email)
    time.sleep(1) # Small delay to avoid rate limiting

print("\n--- Active Accounts ---")
for a in active:
    print(a)
