#!/usr/bin/python3

import subprocess
import json
import os
import sys

NB_BILLS = 0


def process(cmd):
    """
    Run shell commands
    """
    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode == 0:
        return True, process.stdout.decode("utf-8")
    else:
        print(process.stderr.decode("utf-8"))
        return False, ""


def verify_signature(signature, message):
    """
    """
    # Convertir le certificat en binaire
    with open("tmp.sign", "wb") as f:
        f.write(signature.encode("latin-1"))

    # Vérification du certificat du client
    ok, _ = process(
        f"(echo {message} > from.tmp && openssl dgst -sha1 -verify keys/banque.pub -signature tmp.sign from.tmp)")

    _, _ = process("rm from.tmp tmp.sign")

    return ok


def is_bill_exists(bill_number):
    """
    """
    try:
        os.listdir("checks").index(str(bill_number))
        return True
    except ValueError:
        return False


def init():
    """
    """
    ok, _ = process("mkdir -p checks rejected accepted bills")
    return ok


def clean():
    """
    """
    ok, _ = process("rm -rf checks rejected accepted bills")
    return ok


def send_bill(user, amount):
    """
    """
    global NB_BILLS
    NB_BILLS += 1

    # Création de la facture
    with open("facture.json", "w") as f:
        f.write(json.dumps({
            "shop_name": user["name"],
            "amount": amount,
            "bill_number": NB_BILLS,
            "shop_signature": user["signature"]
        }))

    # Hashage de la facture + secret du commercant
    ok, hashed = process(
        f"(cat facture.json && echo {user['hashed_secret']}) | sha256sum")
    if not ok:
        return False
    hashed = hashed.split(" ")[0]

    # Archivage de la facture
    ok, _ = process(f"echo {hashed} > bills/{NB_BILLS}")
    if not ok:
        return False

    # Envoi de la facture au client
    ok, _ = process(f"mv facture.json ../client/bills/{hashed}.json")

    return ok


def verify_check(user, path):
    """
    verify if a bank check is valid
    """
    # Convertir le check en ditionnaire
    with open(path, "r") as f:
        check = json.load(f)

    # Vérification du certificat du client
    if not verify_signature(check["signature"], check['from']):
        return False

    # Verification de l'existence de la facture
    if not is_bill_exists(check["bill_number"]):
        return False

   # Formation de la facture à partir du check
    with open("facture.json", "w") as f:
        f.write(json.dumps({
            "shop_name": check["shop_name"],
            "amount": check["amount"],
            "bill_number": check["bill_number"],
            "shop_signature": check["shop_signature"]
        }))

    # Hashage de la facture + secret du commercant
    ok, hashed = process(
        f"(cat facture.json && echo {user['hashed_secret']}) | sha256sum")
    if not ok:
        return False
    hashed = hashed.split(" ")[0]

    # Vérification de la facture reconstituée
    ok, _ = process(
        f"echo {hashed} > hashed.tmp && diff hashed.tmp bills/{check['bill_number']}")

    _, _ = process(f"rm hashed.tmp")

    return ok


def verify_checks(user):
    """
    Sort checks according if they are accepted or not
    Refused one are stored in the rejected directory
    Valid one are stored in the accepted directory
    """
    checks = os.listdir("checks")

    cpt = 0
    for check in checks:
        if verify_check(user, f"checks/{check}"):
            cpt += 1
            ok, _ = process(f"mv checks/{check} accepted/")
            if not ok:
                return False
        else:
            ok, _ = process(f"mv checks/{check} rejected/")
            if not ok:
                return False

    print(f"+ Chèques valides: {cpt}/{len(checks)}")
    return True


def send_checks():
    """
    Send accepted checks to the bank
    """
    ok, _ = process(
        "mv accepted/* ../bank/checks/")
    return ok


if __name__ == "__main__":

    with open("user.json", "r") as f:
        user = json.load(f)

    if sys.argv[1] == "init":
        ok = init()
        print(
            "+ Commerçant créé avec succès") if ok else print("- Commerçant non créé")

    elif sys.argv[1] == "clean":
        ok = clean()
        print(
            "+ Commerçant effacé avec succès") if ok else print("- Commerçant non effacé")

    if sys.argv[1] == "verify":
        ok = verify_checks(user)
        print(
            "+ Vérification faites avec succès") if ok else print("- Chèques non vérifiés")

    elif sys.argv[1] == "checks":
        ok = send_checks()
        print("+ Chèques envoyés avec succès") if ok else print("- Chèques non envoyés")

    elif sys.argv[1] == "bill":
        ok = send_bill(user, int(sys.argv[2]))
        print("+ Facture envoyée avec succès") if ok else print("- Facture non envoyée")
