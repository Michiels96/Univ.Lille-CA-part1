#!/usr/bin/python3

import subprocess
import json
import os
import sys


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


def init():
    """
    """
    ok, _ = process("mkdir -p checks rejected accepted")
    return ok


def clean():
    """
    """
    ok, _ = process("rm -rf checks rejected accepted")
    return ok


def verify_check(user, path):
    """
    verify if a bank check is valid
    """
    # Convertir le check en ditionnaire
    with open(path, "r") as f:
        check = json.load(f)

    # Convertir le certificat en binaire
    with open("tmp.sign", "wb") as f:
        f.write(check["certificate"].encode("latin-1"))

    # Vérification du certificat du client
    ok, _ = process(
        f"(echo {check['from']} > from.tmp && openssl dgst -sha1 -verify ../banque/keys/banque.pub -signature tmp.sign from.tmp)")

    _, _ = process("rm from.tmp tmp.sign")

    return ok and user["name"] == check["to"]


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
        "mv accepted/* ../banque/checks/")
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
    elif sys.argv[1] == "send":
        ok = send_checks()
        print("+ Chèques envoyés avec succès") if ok else print("- Chèques non envoyés")
