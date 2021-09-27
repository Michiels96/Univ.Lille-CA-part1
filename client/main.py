#!/usr/bin/python3


import subprocess
import json
import datetime as dt
import argparse


def process(cmd):
    """
    """
    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode == 0:
        return True, process.stdout.decode("utf-8")
    else:
        print(process.stderr.decode("utf-8"))
        return False, ""


def send_check(user, amount, to):
    """
    """
    # Création du chèque
    with open("check.json", "w") as f:
        f.write(json.dumps({
            "from": user["name"],
            "to": to,
            "amount": amount,
            "date": dt.datetime.now().isoformat(),
            "certificate": user["certificate"]
        }))

    # Hashage du chèque + secret du client
    ok, hashed = process(
        f"(cat check.json && echo {user['hashed_secret']}) | sha256sum")
    if not ok:
        return False
    hashed = hashed.split(" ")[0]

    # Envoi du chèque au commerçant
    ok, _ = process(f"mv check.json ../shop/checks/{hashed}.json")
    return ok


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description="Send check to a shop"
    )
    parser.add_argument(
        "-amount",
        type=int,
        required=True,
        help="Set the amount of the check",
    )

    parser.add_argument(
        "-to",
        type=str,
        required=True,
        help="Set the recipient of the check",
    )
    args = parser.parse_args().__dict__

    with open("user.json", "r") as f:
        user = json.load(f)

    ok = send_check(user, args["amount"], args["to"])
    print("+ Chèque envoyé avec succès") if ok else print("- Chèque non envoyé")
