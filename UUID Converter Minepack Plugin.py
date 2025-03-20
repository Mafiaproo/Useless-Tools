# Importation des librairies nécessaires
import sqlite3  # Pour la gestion des bases de données SQLite
import requests  # Pour faire des requêtes HTTP (API Mojang)
import json  # Pour manipuler les données JSON
import colorama, uuid  # Pour ajouter des couleurs au terminal et gérer les UUIDs
from colorama import Fore, Back, Style  # Importation spécifique des couleurs de colorama
import time  # Pour gérer les pauses entre les requêtes

# Définition d'un namespace UUID utilisé pour générer des UUID hors-ligne
namespace = uuid.NAMESPACE_DNS  

# Liste vide pour stocker les résultats (liste de tuples)
datas = [()]

# Fonction pour générer un UUID hors-ligne pour les joueurs crackés
def generate_offline_uuid(username):
    return uuid.uuid3(uuid.NAMESPACE_DNS, f"OfflinePlayer:{username}").hex

# Connexion à la base de données "backpack.db"
db = sqlite3.connect('backpack.db')
cursor = db.cursor()

# Sélection de tous les joueurs de la table "backpack_players"
lists = cursor.execute('SELECT * FROM backpack_players')
lists = cursor.fetchall()  # Récupération des données sous forme de liste

# Affichage des joueurs récupérés
print(lists)

# Fermeture de la connexion à la base de données
db.close()

# Ouverture d'une nouvelle connexion à la base de données "out.db" pour mettre à jour les UUIDs
db = sqlite3.connect('out.db')
cursor = db.cursor()

# Parcours de la liste des joueurs récupérés
for player in lists:

    owner_id = player[0]  # ID du joueur dans la base de données
    username = player[1]  # Nom du joueur
    old_uuid = player[2]  # Ancien UUID du joueur
    new_uuid = None  # Initialisation du nouvel UUID à None

    # Affichage de l'ancien UUID du joueur
    print(Fore.BLUE + "OLD " + username + " uuid: " + old_uuid)

    try:
        # Tentative de récupération du nouvel UUID en interrogeant l'API Mojang
        for i in range(0, 3):  # Trois tentatives en cas d'échec
            print(Fore.YELLOW + "fetching data...")

            # Requête API pour récupérer l'UUID du joueur
            data = requests.get(f"https://api.mojang.com/users/profiles/minecraft/{username}")

            # Pause pour éviter d'envoyer trop de requêtes rapidement
            time.sleep(0.05)

            # Affichage des données reçues
            print(Fore.YELLOW + "Data: " + str(data.json()))

            # Vérification si l'UUID est présent dans la réponse
            if "id" in data.json():
                new_uuid = data.json()["id"]
                break  # Sortie de la boucle si l'UUID a été trouvé

        # Si un nouvel UUID est trouvé, mise à jour dans la base de données
        if "id" in data.json():
            print(Fore.LIGHTGREEN_EX + "NEW " + username + " : " + str(data.json()["id"]))

            # Mise à jour de l'UUID du joueur dans la base de données
            cursor.execute(f"UPDATE backpack_players SET uuid = '{new_uuid}' WHERE player_id = '{owner_id}'")
            db.commit()

            # Affichage de confirmation
            print(Fore.MAGENTA + "Player " + username + " UUID updated succesfully. Old UUID: " + old_uuid + " New UUID: " + new_uuid)

            # Ajout aux données traitées
            datas.append((username, new_uuid))

        else:
            # Si l'UUID n'est pas trouvé, on considère que le joueur est soit en Bedrock soit Cracké
            print(Fore.RED + "ATTENTION " + username + " : " + "Joueur Bedrock ou Crack")

            # Détection des joueurs Bedrock (les pseudos contiennent souvent un point)
            if "." in username:
                print(Fore.RED + "Joueur Bedrock\n")
                datas.append((username, old_uuid))

            else:
                # Génération d'un UUID hors-ligne pour les joueurs Crackés
                new_uuid = generate_offline_uuid(username=username)

                print(Fore.LIGHTGREEN_EX + "NEW " + username + " : " + str(new_uuid))

                # Mise à jour de l'UUID dans la base de données
                cursor.execute(f"UPDATE backpack_players SET uuid = '{str(new_uuid)}' WHERE player_id = '{owner_id}'")
                db.commit()

                # Affichage de confirmation
                print(Fore.LIGHTBLUE_EX + "Player " + username + " UUID generated succesfully for cracked player. Old UUID: " + old_uuid + " New UUID: " + str(new_uuid))

                # Ajout aux données traitées
                datas.append((username, new_uuid))

        # Saut de ligne pour la lisibilité
        print("\n ")
    
    except Exception as e:
        # Gestion des erreurs lors du traitement d'un joueur
        print(Fore.RED + "Un problème est survenu lors du traitement de : " + username + "\nErreur: \n" + str(e))

# Affichage des données traitées
print(datas)
print(Fore.RESET + "\n\n")

# -------------------- Vérification des données mises à jour --------------------

# Sélection des données traitées dans la base de données
datasToValidate = cursor.execute('SELECT * FROM backpack_players')

i = 0  # Compteur de validation
erreurs = []  # Liste pour stocker les erreurs détectées

# Vérification des données en base avec les données mises à jour
for data in datasToValidate:
    i += 1

    # Comparaison des données stockées et des mises à jour
    if datas[i][0] == data[1] and datas[i][1] == data[2]:
        print(Fore.LIGHTGREEN_EX + "Data " + str(i) + " is correct")
    else:
        print(Fore.RED + "Data " + str(i) + " is incorrect")
        erreurs.append(str(data[1]))  # Ajout du pseudo concerné à la liste des erreurs

# Affichage des erreurs détectées
if len(erreurs) > 0:
    print(Fore.RED + "Erreurs: " + str(erreurs))

# Fermeture de la base de données
db.close()

# Réinitialisation des couleurs de la console
print(Fore.RESET)
