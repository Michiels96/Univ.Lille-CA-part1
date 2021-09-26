#!/home/baht/env/bin/python3

#
#
#

import subprocess
import json


def process(cmd):
    """
    """
    process = subprocess.run(cmd, capture_output=True, shell=True)
    if process.returncode == 0:
        return True, process.stdout.decode("utf-8")
    else:
        print(process.stderr.decode("utf-8"))
        return False, ""


def create_banque():
    """
    """
    ok, _ = process("mkdir -p keys")
    if not ok:
        return False

    ok, _ = process("openssl genrsa -out keys/banque.rsa 2048")
    if not ok:
        return False

    ok, _ = process(
        "openssl rsa -in keys/banque.rsa -outform PEM -pubout -out keys/banque.pub")
    if not ok:
        return False


def create_user():
    """
    """
    name = input("Enter your name: ")
    ok, hashed_name = process(f"echo {name} | sha256sum")
    if not ok:
        return {}
    hashed_name = hashed_name.split(" ")[0]

    ok, _ = process(f"openssl genrsa -out keys/{hashed_name}.rsa 2048")
    if not ok:
        print("error")
        return {}

    ok, _ = process(
        f"echo {hashed_name} > hashed_name.tmp && openssl dgst -sha1 -sign keys/banque.rsa -out certificate.sign hashed_name.tmp && rm hashed_name.tmp")
    if not ok:
        return {}

    ok, private_key = process(f"cat keys/{hashed_name}.rsa")
    if not ok:
        return {}

    with open("certificate.sign", "rb") as f:
        certificate = f.read()

    ok, _ = process(f"rm certificate.sign")

    with open("user.json", "w") as f:
        f.write(json.dumps({
            "name": name,
            "hashed_name": hashed_name,
            "private_key": private_key,
            "certificate": certificate.decode("latin-1")
        }))


if __name__ == "__main__":
    print("------------- BANQUE -------------")
    create_banque()

    while True:
        print("\n=> MENU")
        print("1: Créer un client")
        print("2: Créer un commerçant")
        try:
            choice = int(input("Votre choix: "))
            dir = "client" if choice == 1 else "shop"
            create_user()
            ok, _ = process(f"mv user.json ../{dir}/")
            if ok:
                print("+ Utilisateur créé avec succès")
        except ValueError as err:
            print(err)
