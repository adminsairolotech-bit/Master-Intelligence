import imaplib
import time

accounts = [
    "nycossferdulay@outlook.com", "veveccacopriv@outlook.com", "beiringbickumq@outlook.com",
    "razaigawliy@outlook.com", "prescillaspiottot@outlook.com", "tobeikamiraveti@outlook.com",
    "trussogeuidaf@outlook.com", "biulatorviky@outlook.com", "tanykiayijieg@outlook.com",
    "nimangorbass@outlook.com", "manafyciganekb@outlook.com", "meixiadayellc@outlook.com",
    "risolecilliet@outlook.com", "zijahumarahm@outlook.com", "breznykeolkerv@outlook.com",
    "doulykulaya95@outlook.com", "lobleantuazzf@outlook.com", "dezelanchaloeil@outlook.com",
    "tarlonpatikk@outlook.com", "deoudeskahiapoh@outlook.com"
]
password = "groksuper123@"

print("Checking accounts via IMAP...")
active = []
for email in accounts:
    try:
        # Outlook IMAP server
        mail = imaplib.IMAP4_SSL("outlook.office365.com")
        mail.login(email, password)
        print(f"{email}: SUCCESS")
        active.append(email)
        mail.logout()
    except imaplib.IMAP4.error as e:
        print(f"{email}: FAILED ({str(e)})")
    except Exception as e:
        print(f"{email}: ERROR ({str(e)})")
    
    time.sleep(0.5)

print("\n--- Verified Active Accounts ---")
for a in active:
    print(a)
