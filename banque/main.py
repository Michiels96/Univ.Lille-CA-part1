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


def hash(cmd):
    ok, hashed = process(cmd)
    if not ok:
        return False, ""
    return True, hashed.split(" ")[0]


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


def create_client(name):
    """
    """

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
        f"echo {name} > name.tmp && openssl dgst -sha1 -sign keys/banque.rsa -out certificate.sign name.tmp && rm name.tmp")
    if not ok:
        return {}

    # Parsing du certificat en un format transportable
    with open("certificate.sign", "rb") as f:
        certificate = f.read()

    ok, _ = process(f"rm certificate.sign")

    return {
        "name": name,
        "hashed_secret": hashed_secret,
        "certificate": certificate.decode("latin-1")
    }


def create_shop(name):
    """
    """

    # Récuperation de la clef publique de la banque
    ok, banque_pub = process(f"cat keys/banque.pub")
    if not ok:
        return {}

    return {
        "name": name,
        "banque_pub_key": banque_pub
    }


if __name__ == "__main__":
    print("-------------- BANQUE --------------")
    create_banque()

    while True:
        print("\n=> MENU")
        print("1: Créer un client")
        print("2: Créer un commerçant")
        try:
            choice = int(input("Votre choix: "))
            name = input("Entrez votre nom: ")
            if (choice > 0 and choice < 3):
                if choice == 1:
                    dir = "client"
                    user = create_client(name)
                else:
                    dir = "shop"
                    user = create_shop(name)

                with open("user.json", "w") as f:
                    f.write(json.dumps(user))

                ok, _ = process(f"mv user.json ../{dir}/")
                if ok:
                    print("+ Utilisateur créé avec succès")
        except ValueError:
            print("Veuillez saisir soit 1 ou 2")
