# To do :

1. Il ne faut pas modifier le simulateur petzi
2. L'app doit pouvoir afficher que le chargement est en attente ...
* On se connecte à python petzi_simulator.py http://127.0.0.1:5000/webhook
* Le serveur vérifie que c'est bien petzi qui se connecte (voir PETZI-Webhook.pdf)
* Il persiste les données pour traitement / Il sauvegarde les données, idéalement pas en fichier json quoi...
3. Le serveur affiche que les données ont bien été chargées

Demarrér le serveur: python app.py
Lancer le webhook: python petzi_simulator.py http://127.0.0.1:5000/webhook
Visualiser la bd: http://127.0.0.1:5000/database