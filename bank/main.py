#!/usr/bin/python3

import subprocess
import json
import os
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


def hash(cmd):
    ok, hashed = process(cmd)
    if not ok:
        return False, ""
    return True, hashed.split(" ")[0]


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


def create_banque():
    """
    Creation of the banque
    """
    ok, _ = process("mkdir -p keys checks rejected accepted")
    if not ok:
        return False

    ok, _ = process("openssl genrsa -out keys/banque.rsa 2048")
    if not ok:
        return False

    ok, _ = process(
        "openssl rsa -in keys/banque.rsa -outform PEM -pubout -out keys/banque.pub")
    return ok


def delete_banque():
    """
    Delete the banque
    """
    ok, _ = process("rm -rf keys checks rejected accepted")
    return ok


def create_user(name):
    """
    Creation of a client with the given name
    """
    # Récuperation de la clef publique de la banque
    ok, banque_pub = process(f"cat keys/banque.pub")
    if not ok:
        return {}

    # Hashage du nom de l'utilisateur
    ok, hashed_name = hash(f"echo {name} | sha256sum")
    if not ok:
        return {}

    # Génération du secret de l'utilisateur
    ok, _ = process(
        f"dd if=/dev/urandom of=keys/{hashed_name}.secret bs=32 count=1")
    if not ok:
        return {}

    # Hashage du secret du client
    ok, hashed_secret = hash(f"cat keys/{hashed_name}.secret | sha256sum")
    if not ok:
        return {}

    # Création du certificat du client
    ok, _ = process(
        f"echo {name} > name.tmp && openssl dgst -sha1 -sign keys/banque.rsa -out signature.sign name.tmp && rm name.tmp")
    if not ok:
        return {}

    # Parsing du certificat en un format transportable
    with open("signature.sign", "rb") as f:
        signature = f.read()

    ok, _ = process(f"rm signature.sign")

    return {
        "name": name,
        "hashed_secret": hashed_secret,
        "banque_pub_key": "\n" + banque_pub,
        "signature": signature.decode("latin-1")
    }


def verify_check(path):
    """
    """
    # Convertion du chèque en ditionnaire
    with open(path, "r") as f:
        check = json.load(f)

    # Verify cient signature
    if not verify_signature(check["client_signature"], check["from"]):
        return False

    # Verify shop signature
    if not verify_signature(check["shop_signature"], check["to"]):
        return False

    # Hashage du nom de l'utilisateur
    ok, hashed_name = hash(f"echo {check['from']} | sha256sum")
    if not ok:
        False

    # Hashage du secret du client
    ok, hashed_secret = hash(f"cat keys/{hashed_name}.secret | sha256sum")
    if not ok:
        return False

    # Hashage du chèque + secret hashé du client
    ok, hashed = hash(
        f"(cat {path} && echo {hashed_secret}) | sha256sum")

    return ok and hashed == os.path.basename(path).split(".")[0]


def verify_checks():
    """
    Sort checks according if they are accepted or not
    Refused one are stored in the rejected directory
    Valid one are stored in the accepted directory
    """
    checks = os.listdir("checks")

    cpt = 0
    for check in checks:
        if verify_check(f"checks/{check}"):
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


if __name__ == "__main__":

    if sys.argv[1] == "init":
        ok = create_banque()
        print(
            "+ Banque créee avec succès") if ok else print("- Banque non créee")

    elif sys.argv[1] == "clean":
        ok = delete_banque()
        print(
            "+ Banque effacée avec succès") if ok else print("- Banque non effacée")

    elif sys.argv[1] == "client":
        with open("user.json", "w") as f:
            f.write(json.dumps(create_user(sys.argv[2])))
        ok, _ = process(f"mv user.json ../client/")
        if ok:
            print("+ Client créé avec succès")

    elif sys.argv[1] == "shop":
        with open("user.json", "w") as f:
            f.write(json.dumps(create_user(sys.argv[2])))
        ok, _ = process(f"mv user.json ../shop/")
        if ok:
            print("+ Commerçant créé avec succès")

    elif sys.argv[1] == "verify":
        ok = verify_checks()
        print(
            "+ Vérification faites avec succès") if ok else print("- Chèques non vérifiés")
