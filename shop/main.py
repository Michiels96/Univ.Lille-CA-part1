#!/home/baht/env/bin/python3

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


def verify_check(filename):
    """
    verify if a bank check is valid
    """
    # Convertir le check en ditionnaire
    with open(filename, "r") as f:
        check = json.load(f)

    # Convertir le certificat en binaire
    with open("tmp.sign", "wb") as f:
        f.write(check["certificate"].encode("latin-1"))

    # Vérification du certificat du client
    ok, _ = process(
        f"(echo {check['from']} > from.tmp && openssl dgst -sha1 -verify ../banque/keys/banque.pub -signature tmp.sign from.tmp)")

    _, _ = process("rm from.tmp tmp.sign")

    return ok


def verify_checks():
    """
    Sort checks according if they are accepted or not
    Refused one are stored in the rejected directory
    Valid one are stored in the accepted directory
    """
    ok, _ = process("mkdir -p rejected accepted")
    if not ok:
        return False

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


def send_checks():
    """
    Send accepted checks to the bank
    """
    ok, _ = process(
        "mv accepted/* ../banque/checks/ && rm -rf accepted rejected")
    return ok


if __name__ == "__main__":

    _, _ = process("mkdir -p checks")

    with open("user.json", "r") as f:
        user = json.load(f)

    if sys.argv[1] == "verify":
        ok = verify_checks()
        print(
            "+ Vérification faites avec succès") if ok else print("- Chèques non vérifiés")
    elif sys.argv[1] == "send":
        ok = send_checks()
        print("+ Chèques envoyés avec succès") if ok else print("- Chèques non envoyés")
