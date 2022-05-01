import pyotp, pyAesCrypt, io, os, time, datetime, json

BUFFER_SIZE = 4096

OPTION_TEXT = """Options:
1: Choose account to display 2fa for
2: Add more 2fa accounts
3: List all accounts
4: Exit
"""


def create_account() -> "tuple[str]":
    secret = input("What 16-character secret was given to you? ").replace(" ", "")
    name = input("Give a name for this account: ")
    return secret, name

def sync_json_to_secret_file(json_data: "dict[str, dict[str, str]]") -> None:
    secret_buf = io.BytesIO()
    secret_buf.write(json.dumps(json_data).encode("utf-8"))
    secret_buf.seek(0)
    with open("secret", "wb") as f:
        pyAesCrypt.encryptStream(secret_buf, f, passw, BUFFER_SIZE)

if not os.path.exists("secret"):
    secret, name = create_account()
    passw = input(
        "Enter a password to encrypt the secret (if you forget, there is no recovery!): "
    )

    json_data = {"account-store": {name: secret}}
    secret_bytes = json.dumps(json_data).encode("utf-8")
    buffer = io.BytesIO()
    buffer.write(secret_bytes)
    buffer.seek(0)
    with open("secret", "wb") as f:
        pyAesCrypt.encryptStream(buffer, f, passw, BUFFER_SIZE)
else:
    secret_buf = io.BytesIO()
    passw = input("Enter your password: ")
    size = os.stat("secret").st_size
    with open("secret", "rb") as f:
        pyAesCrypt.decryptStream(
            f, secret_buf, passw, BUFFER_SIZE, size
        )
    secret_buf.seek(0)
    json_data: "dict[str, dict[str, str]]" = json.loads(secret_buf.read().decode("utf-8"))

while True:
    res = int(input(OPTION_TEXT).strip())
    while res not in [1, 2, 3, 4]:
        print("Invalid option")
        res = int(input(OPTION_TEXT).strip())
    if res == 1:
        while True:
            account = input("Which account do you want to display 2fa for? ")
            try:
                otp = pyotp.TOTP(json_data["account-store"][account])
                break
            except KeyError:
                print("No account exists")
        try:
            while True:
                print(
                    f"Discord 2fa token: {otp.now()}, {round(otp.interval - datetime.datetime.now().timestamp() % otp.interval, 1)} seconds left",
                    end="",
                )
                time.sleep(0.1)
                print("\r", end="")
        except KeyboardInterrupt:
            pass
    elif res == 2:
        secret, name = create_account()
        json_data["account-store"][name] = secret
        sync_json_to_secret_file(json_data)
    elif res == 3:
        for key in json_data["account-store"]:
            print("Account with name:", key)
    elif res == 4:
        print("Exiting...")
        exit()
