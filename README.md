# 🎟️ TicketHub App

---

## 🚀 Démarrer le serveur :

```bash
python app.py

## 🛠️ Lancer le webhook (pour créer une commande) :
```bash
python petzi_simulator.py http://127.0.0.1:5000/webhook

### 📊 Visualiser la base de données :
```bash
http://127.0.0.1:5000/database

## 🐳 Base de données avec Docker Compose
### Démarrer : 
```bash
docker-compose up -d

### Vérifier l'exécution : 
```bash
docker ps

### Connexion : 
```bash
mysql -h 127.0.0.1 -P 3306 -u myuser -p

### Mot de passe : 
```bash
mypassword

### Arrêter : 
```bash
docker-compose down

### 📄 Voir les données de la table:
```bash 
SELECT * FROM tickets;

### 🗑️ Supprimer les données de la table: 
```bash
DELETE FROM tickets;

