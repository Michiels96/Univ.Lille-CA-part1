#!/usr/bin/python3


import subprocess
import json
import sys


def process(cmd):
    """
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
        f"(echo {message} > from.tmp && openssl dgst -sha1 -verify banque.pub -signature tmp.sign from.tmp)")

    _, _ = process("rm from.tmp tmp.sign")

    return ok


def init(user):
    """
    """
    ok, _ = process(
        f"cat > banque.pub << EOF && echo -e {user['banque_pub_key']}")
    if not ok:
        return False

    ok, _ = process("mkdir -p rejected paid bills")
    return ok


def clean():
    """
    """
    ok, _ = process("rm -rf rejected paid bills banque.pub")
    return ok


def get_bill_file(bill_name):
    """
    """
    # Convertion de la facture en ditionnaire
    with open(f"bills/{bill_name}", "r") as f:
        bill = json.load(f)

    # Vérification du certificat du commercant
    return verify_signature(bill["shop_signature"], bill['shop_name']), bill


def send_check(user, to, bill_number):
    """
    """
    # format fichier: {shop_name}_{bill_number}.json
    # Recuperation et verification de la facture
    verified, bill = get_bill_file(f"{to}_{bill_number}.json")
    if not verified:
        _, _ = process(f"mv bills/{to}_{bill_number}.json rejected/")
        return False

    # Création du chèque
    with open("check.json", "w") as f:
        f.write(json.dumps({
            "from": user["name"],
            "to": to,
            "amount": bill["amount"],
            "bill_number": bill["bill_number"],
            "client_signature": user["signature"],
            "shop_signature": bill["shop_signature"],
        }))

    # Hashage du chèque + secret du client
    ok, hashed = process(
        f"(cat check.json && echo {user['hashed_secret']}) | sha256sum")
    if not ok:
        return False
    hashed = hashed.split(" ")[0]

    # Envoi du chèque au commerçant
    ok, _ = process(f"mv check.json ../shop/checks/{hashed}.json")

    _, _ = process(f"mv bills/{to}_{bill_number}.json paid/")
    return ok


if __name__ == "__main__":

    with open("user.json", "r") as f:
        user = json.load(f)

    if sys.argv[1] == "init":
        ok = init(user)
        print(
            "+ Commerçant créé avec succès") if ok else print("- Commerçant non créé")

    elif sys.argv[1] == "clean":
        ok = clean()
        print(
            "+ Commerçant effacé avec succès") if ok else print("- Commerçant non effacé")

    elif sys.argv[1] == "check":
        ok = send_check(user, sys.argv[2], int(sys.argv[3]))
        print("+ Chèque envoyé avec succès") if ok else print("- Chèque non envoyé")
