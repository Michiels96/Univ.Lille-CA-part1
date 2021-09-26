#!/home/baht/env/bin/python3

#
#
#

import subprocess
import json
import datetime as dt


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
    ok, _ = process(f"mv check.json ../shop/{hashed}.json")
    return ok


if __name__ == "__main__":
    with open("user.json", "r") as f:
        user = json.load(f)

    print("-------------- CLIENT --------------")
    print("=> Envoi de chèque")

    try:
        to = input("Destinataire: ")
        amount = int(input("Montant: "))
        ok = send_check(user, amount, to)
        print("+ Chèque envoyé avec succès") if ok else print("- Chèque non envoyé")
    except ValueError as err:
        print(err)
