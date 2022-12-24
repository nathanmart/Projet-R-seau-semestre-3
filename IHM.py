import socket
import time

# Connexion TCP au programme gestion.py
sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST_client, PORT_client = 'localhost', 10000
sock_client.connect((HOST_client, PORT_client))
print("Connexion établie sur " + str(HOST_client) + "@" + str(PORT_client))

# Configuration serveur HTML
sock_HTML = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
HOST_HTML, PORT_HTML = 'localhost', 10001
sock_HTML.bind((HOST_HTML, PORT_HTML))
sock_HTML.listen(1)

while True:
    info = []

    # Reception des infos du programme gestion
    recu = sock_client.recv(1024).decode()

    # En cas d'envoie multiple, recipère seulement le dernier message
    recu = recu.split(';')
    recu = recu[-1]

    data = []
    for i in range(0, 7):
        data.append([])
        temporaire = recu[i].split(",")
        for j in range(0, len(temporaire)):
            data[i].append(temporaire[j])

    try:
        # Attente de connexion client
        print("Attente de client")
        connexion_HTML, client_adresse_HTML = sock_HTML.accept()
        print("Client connecté")
        connexion_HTML.recv(1024)

        # Envoie entête HTML
        connexion_HTML.send("HTTP/1.0 200 OK\n".encode())
        connexion_HTML.send('Content-Type: text/html\n'.encode())
        connexion_HTML.send('\n'.encode())

        # Création du message
        message = \
        """
        <html>
            <meta charset="UTF-8">
            <meta http-equiv="refresh" content="10">
            <head>
            <style>
                table{
                    border-collapse: collapse
                }
        
                td{
                    border: 1px solid black;
                    padding: 10px
                }
            </style>
            </head>
        
            <body>
                <h1>Gestion de la Pizzeria</h1>
        
                <p>Nombre de pizzas commandées """ + str(data[0][0]) + """</p>
                <p>Nombre de pizzas refusées """ + str(data[0][1]) + """</p>
                <p>Nombre de pizzas préparées """ + str(data[0][2]) + """</p>
        
                <table>
                    <tr>
                        <td><strong>Numéro de poste</strong></td>
                        <td><strong>Nombre de pizza en préparation</strong></td>
                        <td><strong>Capacité de production max</strong></td>
                        <td><strong>Etat de fonctionnement</strong></td>
                    </tr>
        
                    <tr>
                        <td>N°1</td>
                        <td>>""" + str(data[1][0]) + """</td>
                        <td>>""" + str(data[1][1]) + """</td>
                        <td>>""" + str(data[1][2]) + """</td>
                    </tr>
        
                    <tr>
                        <td>N°2</td>
                        <td>>""" + str(data[2][0]) + """</td>
                        <td>>""" + str(data[2][1]) + """</td>
                        <td>>""" + str(data[2][2]) + """</td>
                    </tr>
        
                    <tr>
                        <td>N°3</td>
                        <td>>""" + str(data[3][0]) + """</td>
                        <td>>""" + str(data[3][1]) + """</td>
                        <td>>""" + str(data[3][2]) + """</td>
                    </tr>
        
                    <tr>
                        <td>N°4</td>
                        <td>>""" + str(data[4][0]) + """</td>
                        <td>>""" + str(data[4][1]) + """</td>
                        <td>>""" + str(data[4][2]) + """</td>
                    </tr>
        
                    <tr>
                        <td>N°5</td>
                        <td>>""" + str(data[5][0]) + """</td>
                        <td>>""" + str(data[5][1]) + """</td>
                        <td>>""" + str(data[5][2]) + """</td>
                    </tr>
        
                    <tr>
                        <td>N°6</td>
                        <td>>""" + str(data[6][0]) + """</td>
                        <td>>""" + str(data[6][1]) + """</td>
                        <td>>""" + str(data[6][2]) + """</td>
                    </tr>
                </table>
            </body>
        </html>
        """

        # Envoie du message
        connexion_HTML.send(message.encode())
        connexion_HTML.close()
        print("Message envoyé sur le navigateur")

    except:
        connexion_HTML.close()
        print("ERREUR")

    time.sleep(1)