import datetime
import socket
import psycopg2

dbname = 'PROJET_PEI'
password = "pguser"
user = 'pguser'


# Vérifie que le timing pour la création
def check_timing(ID, nom_pizza, taille, heure_livraison, heure_commande):
    # Récupère la distance avec le client
    cur.execute("SELECT \"Distance\" FROM \"Client\" WHERE \"ID\" = " + ID)
    distance = cur.fetchall()[0][0]

    # Récupère le temps de production
    cur.execute(
        "SELECT \"TPsProd\" FROM \"Pizza\" WHERE \"Nom\" = '" + nom_pizza + "' AND \"Taille\" = '" + taille + "'")
    temps_production = cur.fetchall()[0][0]

    # Calcul le temps total
    temps_total = distance + temps_production

    # Calcul le temps de marge
    difference = (heure_livraison - datetime.timedelta(minutes=temps_total)) - heure_commande

    # Si marge positive, c'est faisable
    if (difference >= datetime.timedelta(0)):
        return True, (heure_commande + datetime.timedelta(minutes=temps_total))
    else:
        return False, False


# Check si les pizzas sont prêtes, les supprime dans le cas échéant
def liberer_place(heure):
    # Parcourt chaque poste
    for poste in gestion:
        # Variable pour ajuster l'index en fonction du nombre de suppressions
        a = 0
        # Parcourt les pizzas
        for i in range(0, len(poste)):
            # Compare l'heure de fin de préparation avec l'heure actuelle
            pizza = poste[i - a]
            heure_pizza = pizza[2]
            difference = heure_pizza - heure

            # Si la différence est négative, c'est que la pizza est prête
            if (difference <= datetime.timedelta(0)):
                # Supprime la pizza
                poste.remove(pizza)
                a += 1
                nb_prepare += 1


# Met à jour les infos des postes
def maj_poste():
    cur.execute("SELECT \"Dispoibilite\", \"Capacite\", FROM \"Production\"")
    i = 0
    for dispo, capacite in cur.fetchall():
        production_max[i] = capacite
        dispo_poste[i] = dispo
        i += 1


# MAIN

# Client UDP
# Ecoute sur le port 30117
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind(('', 30117))

# Connextion au serveur SQL
conn = psycopg2.connect(dbname = dbname, user = user, password = password, host='192.168.30.122', port='5432')
cur = conn.cursor()

# Stockage des pizzas sur les postes
gestion = [[], [], [], [], [], []]

# Informations des postes
production_max = [0, 0, 0, 0, 0, 0]
dispo_poste = [True, True, True, True, True, True]

# Serveur TCP pour la connexion avec l'IHM
serveur_TCP = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST, PORT = 'localhost', 10000
serveur_TCP.bind((HOST, PORT))
serveur_TCP.listen(10)

print("Serveur sur " + str(HOST) + "@" + str(PORT))

# Attente de la connexion TCP
connexion_TCP, client_adresse = serveur_TCP.accept()

# Compteur
global nb_acceptee
global nb_refusee
global nb_prepare

nb_acceptee, nb_refusee, nb_prepare = 0, 0, 0

while True:
    maj_poste()

    # Reception du message
    message, adresse = sock.recvfrom(1024)
    message = message.decode()

    # Split des valeurs
    DH, ID, nom, taille, quantite, heure_livraison = message.split(",")
    date_commande, heure_commande = DH.split(" ")

    # Conversion en format datetime
    heure_commande = datetime.datetime.strptime(heure_commande, '%H:%M:%S')
    heure_livraison = datetime.datetime.strptime(heure_livraison, '%H:%M')

    print("Une commande de " + quantite + " " + nom + " taille " + taille + " est tombée")

    quantite = int(quantite)
    # Check de timing
    timing, heure_fin = check_timing(ID, nom, taille, heure_livraison, heure_commande)

    # Cas où le timing est bon
    if timing:
        # Parcourt les 6 postes
        for i in range(0, 6):
            # Vérifie que le poste n'est pas à sa capacité max
            if (len(gestion[i]) <= (production_max[i] - quantite)):
                # Récupère les infos du poste
                cur.execute("SELECT \"Restriction\", \"Taille\" FROM \"Production\" WHERE \"Poste\" = " + str(i + 1))
                a = cur.fetchall()
                restriction_pizza = a[0][1]
                restriction_taille = [0][2]

                # Si possible sur ce poste
                if (not ((nom in restriction_pizza) or (dispo_poste[i] == False) or (
                        (not restriction_taille in taille) and (not taille == "-")))):
                    for j in range(0, quantite):
                        gestion[i].append([nom, taille, heure_fin])
                        nb_acceptee += 1
                    break
        nb_refusee += 1

    # Cas où le timing n'est pas bon
    else:
        nb_refusee += 1

    # Vérification des pizzas préparées
    liberer_place(heure_commande)

    # Création du message
    message = str(nb_acceptee) + "," + str(nb_refusee) + "," + str(nb_prepare) + ";"
    for i in range(0, 6):
        nb_pizza_poste = str(len(gestion[i]))
        pizza_max = str(production_max[i])
        poste_actif = str(dispo_poste[i])

        message = message + nb_pizza_poste + "," + pizza_max + "," + poste_actif + ";"

    # Envoie du meesage
    message = message.encode()
    connexion_TCP.sendall(message)
    print("Message envoyé")
