# 🎟️ TicketHub App

---

## 🚀 Démarrer le serveur :

```bash
python app.py
```

## 🛠️ Lancer le webhook (pour créer une commande) :
```bash
python petzi_simulator.py http://127.0.0.1:5000/webhook
```

### 📊 Visualiser la base de données :
```bash
http://127.0.0.1:5000/tickets
```

## 🐳 Base de données avec Docker Compose
### Démarrer : 
```bash
docker-compose up -d
```

### Vérifier l'exécution : 
```bash
docker ps
```

### Connexion : 
```bash
docker exec -it mysql_container mysql -u myuser -p
```

### Mot de passe : 
```bash
mypassword
```

### Arrêter : 
```bash
docker-compose down
```

### 📄 Voir les données de la table:
```bash 
SHOW DATABASES ;
USE mydb ;
SELECT * FROM tickets;
```

### 🗑️ Supprimer les données de la table: 
```bash
DELETE FROM tickets;
```
