from __future__ import annotations
import pyotp, pyAesCrypt, io, os, time, datetime, json, getpass
from typing import Optional, Tuple, Dict, Union, NoReturn

BUFFER_SIZE = 4096

OPTION_TEXT = """Options:
1: Choose account to display 2fa for
2: Add more 2fa accounts
3: List all accounts
4: Exit
"""


def create_account(
    quit: bool = False,
) -> "Union[Tuple[Optional[str], Optional[str]], NoReturn]":
    try:
        secret = input("What secret was given to you? ").replace(" ", "")
        name = input("Give a name for this account: ")
        pyotp.TOTP(secret).now()
        return secret, name
    except KeyboardInterrupt:
        if quit:
            exit(1)
        return None, None
    except Exception:
        print("Invalid secret")
        return None, None


def sync_json_to_secret_file(json_data: "Dict[str, Dict[str, str]]") -> None:
    secret_buf = io.BytesIO()
    secret_buf.write(json.dumps(json_data).encode("utf-8"))
    secret_buf.seek(0)
    with open("secret", "wb") as f:
        pyAesCrypt.encryptStream(secret_buf, f, passw, BUFFER_SIZE)


def get_int(prompt: str) -> "Optional[int]":
    try:
        return int(input(prompt))
    except ValueError:
        return None


def list_accounts(data: "Dict[str, Dict[str, str]]") -> None:
    print("Account list:")
    for key in data["account-store"]:
        print("Account with name:", key)


if not os.path.exists("secret"):
    secret, name = None, None

    while not isinstance(secret, str) or not isinstance(name, str):
        secret, name = create_account(True)

    passw = getpass.getpass(
        "Enter a password to encrypt the secret (if you forget, there is no recovery!): "
    )

    json_data: "Dict[str, Dict[str, str]]" = {"account-store": {name: secret}}
    secret_bytes = json.dumps(json_data).encode("utf-8")
    buffer = io.BytesIO()
    buffer.write(secret_bytes)
    buffer.seek(0)
    with open("secret", "wb") as f:
        pyAesCrypt.encryptStream(buffer, f, passw, BUFFER_SIZE)
else:
    secret_buf = io.BytesIO()
    passw = getpass.getpass("Enter your password: ")
    size = os.stat("secret").st_size
    with open("secret", "rb") as file_reader:
        try:
            pyAesCrypt.decryptStream(file_reader, secret_buf, passw, BUFFER_SIZE, size)
        except ValueError:
            print(
                "Incorrect password, or the file is corrupt. If it's corrupt, change the name of the file to not be 'secret'"
            )
            exit(1)
    secret_buf.seek(0)
    json_data: "Dict[str, Dict[str, str]]" = json.loads( # type: ignore
        secret_buf.read().decode("utf-8")
    )

while True:
    res = get_int(OPTION_TEXT)
    while res not in [1, 2, 3, 4]:
        print("Invalid option")
        res = get_int(OPTION_TEXT)
    if res == 1:
        list_accounts(json_data)
        while True:
            account = input("Which account do you want to display 2fa for? ")
            try:
                otp = pyotp.TOTP(json_data["account-store"][account])
                break
            except Exception:
                print("No account exists")
        try:
            while True:
                print(
                    f"Discord 2fa token: {otp.now()}, {round(otp.interval - datetime.datetime.now().timestamp() % otp.interval, 1)} seconds left. (Ctrl+C to break out)",
                    end="",
                )
                time.sleep(0.1)
                print("\r", end="")
        except KeyboardInterrupt:
            print()
    elif res == 2:
        secret, name = create_account()
        if not isinstance(secret, str) or not isinstance(name, str):
            continue
        json_data["account-store"][name] = secret
        sync_json_to_secret_file(json_data)
    elif res == 3:
        list_accounts(json_data)
    elif res == 4:
        print("Exiting...")
        exit()
