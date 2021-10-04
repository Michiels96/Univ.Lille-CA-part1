# CA-2021

## Objectif

Mise en place d'un protocole de chiffrement permettant les micro paiements bancaires, une sorte d'alternative numerique au chèque.

Les entitités impliquées sont:

- La banque
  - Créer des clients
  - Créer des commerçants
  - Encaisser des chèques
- Le client
  - Emettre des chèques
- Le commerçant
  - Vérifier la validité des chèques
  - Envoyer les chèques à la banque

Les contraintes sont:

- La banque ne communique qu'une seule fois avec le client et le commerçant, celà est fait lors de la création de ceux-ci.
- Le commerçant est sûr d'être payé lorsqu'il réçcoit un chèque
- Le client est assuré que son chèque ne sera pas modifier avant encaissement
- Un client ne peut pas faire un chèque au nom d'un autre client
- Fonctionne hors connexion

## Réalisation

Voici une schema du fonctionnement de notre protocole.

![Schéma du protocole](doc/archi.png)

> Un certificat est la signature, avec la clef privée de la banque, du nom du client.

### Création d'un utilisateur

Lors de la création d'un utilisateur, la banque transmet à celui-ci le fichier _user.json_ contenant:

- Le nom de l'utilisateur
- Le hash du secret de l'utilisateur généré par la banque
- La signature du nom de l'utilisateur par la banque
- La clef publique de la banque

### Emission d'une facture par la banque

Une facture est un fichier _json_ contenant: 

- Le nom du commerçant
- Le montant de la facture
- Le numéro de la facture
- La signature du commerçant par la banque

Le nom du fichier transmis du commerçant au client est sous la forme de {Le nom du commerçant}_{le numéro de la facture}.json.

### Emission d'un chèque par le client

Un chèque est un fichier _json_ contenant:

- Les informations de la facture reçues du commerçant
- Le nom du client
- Le certificat du client

Le nom du fichier transmis au commerçant est le hash du resultat de la concatenation du chèque et du hash du secret du client.

Cette façon de nommer le fichier du chèque nous permettra de savoir si le chèque a été modifié au cours de son transit vers la banque car seul le client émetteur du chèque et la banque possèdent le hash du secret permettant retrouver le nom du chèque.

### Vérification de la validité d'un chèque par le commerçant

Tout d'abord, le commerçant extrait les informations lui permettant d'obtenir une facture qu'il vérifie si celle-ci n'a jamais déjà été encaissée et à partir du hash de cette facture obtenue, il vérifie que les informations sont correctes.

À partir de la clef publique de la banque et du nom du client, le commerçant peut verifier la signature du client et donc s'assurer que le client émetteur du chèque est bel et bien client de la banque. Aussi le commerçant vérifie qu'il est le destinataire du chèque.

Il est impossible qu'on encaisse 2 fois le même chèque car une fois qu'un chèque est vérifié et validé, la facture liée à ce chèque est effacée donc les autres chèques n'auront plus de factures correspondantes dans la base de données.

### Envoi des chèques à la banque

Tous les chèques valides sont envoyés à la banque.

### Encaissement d'un chèque par la banque

À partir du secret du client émetteur du chèque et du chèque, la banque peut reconstituer le nom du chèque (le hash du resultat de la concatenation du chèque et du hash du secret du client).
Si cette reconstitution est réussie alors le chèque est valide car la banque est sûre que le chèque n'a pas été modifié depuis l'émission du chèque par le client.

La banque archive les chèques qu'elle à déjà encaissée pour ne pas avoir à encaisser 2 fois le même chèque.

## Utilisation du programme

### banque

Dans le dossier _bank_, lancez les commandes suivantes:

- Création d'une banque
  ```sh
  $ ./main.py init
  ```
- Suppression d'une banque
  ```sh
  $ ./main.py clean
  ```
- Création d'un client
  ```sh
  $ ./main.py client <nom du client>
  ```
- Création d'un commerçant
  ```sh
  $ ./main.py shop <nom du commerçant>
  ```
- Vérification des chèques
  ```sh
  $ ./main.py verify
  ```
  > Les chèques acceptés seront dans les dossier _accepted_ et les autres dans le dossier _rejected_.

### client

Dans le dossier _client_, lancez les commandes suivantes:

- Création d'un client
  ```sh
  $ ./main.py init
  ```
- Suppression d'un client
  ```sh
  $ ./main.py clean
  ```
- Émission d'un chèque
  ```sh
  $ ./main.py check <nom du commerçant> <num. de facture>
  ```
  > Les chèques seront dans le sous dossier _checks_ du dossier _shop_

### commerçant

Dans le dossier _shop_, lancez les commandes suivantes:

- Initialisation
  ```sh
  $ ./main.py init
  ```
- Suppression des dossiers créés lors de l'initialisation

  ```sh
  $ ./main.py clean
  ```

- Vérification des chèques

  ```sh
  $ ./main.py verify
  ```

  > Les chèques acceptés seront dans les dossier _accepted_ et les autres dans le dossier _rejected_.

- Envoi des chèques
  ```sh
  $ ./main.py checks
  ```
  > Les chèques seront dans le sous dossier _checks_ du dossier _bank_.


- Envoi d'une facture
  ```sh
  $ ./main.py bill <montant de la facture>
  ```
