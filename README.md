# 🤖 Bot Tinder Discord

Un bot Discord qui simule l'expérience Tinder directement sur votre serveur ! Les membres peuvent "swiper" sur les profils d'autres utilisateurs et créer des matches.

## ✨ Fonctionnalités

- **Système de Swipe** : Likez (❤️) ou passez (❌) sur les profils des autres membres
- **Matches en temps réel** : Notifications publiques quand deux personnes se likent mutuellement
- **Profils persistants** : Sauvegarde automatique des données dans un fichier JSON
- **Interface interactive** : Boutons Discord pour une expérience utilisateur fluide
- **Statistiques** : Suivez vos likes, passes et matches
- **Contrôle de visibilité** : Activez/désactivez votre profil

## 🚀 Installation et Configuration

### Prérequis
```bash
pip install discord.py
```

### Configuration
1. Créez une application Discord sur le [Portail Développeur Discord](https://discord.com/developers/applications)
2. Remplacez le `TOKEN` dans le code par votre token de bot
3. Invitez le bot sur votre serveur avec les permissions nécessaires

### Permissions nécessaires
- Lire les messages
- Envoyer des messages
- Utiliser les commandes slash
- Voir les membres du serveur
- Intégrer des liens
- Utiliser des emojis externes

## 📝 Commandes Disponibles

| Commande | Description |
|----------|-------------|
| `!swipe` | Commencer une session de swipe |
| `!matches` | Afficher vos matches actuels |
| `!profile` | Voir vos statistiques personnelles |
| `!toggle` | Activer/désactiver votre profil |
| `!reset` | Réinitialiser votre profil (admin uniquement) |
| `!help_tinder` | Afficher l'aide complète |

## 🎮 Comment utiliser

### 1. Commencer à swiper
```
!swipe
```
- Affiche le profil d'un membre aléatoire
- Cliquez sur ❤️ pour liker ou ❌ pour passer
- Le bot propose automatiquement la personne suivante

### 2. Vérifier vos matches
```
!matches
```
- Affiche la liste de toutes vos matches
- Seuls les membres encore présents sur le serveur sont affichés

### 3. Voir vos statistiques
```
!profile
```
- Nombre de likes donnés
- Nombre de passes
- Nombre total de matches
- Statut du profil (actif/inactif)

## 🏗️ Architecture du Code

### Classes principales

#### `TinderBot`
- **Gestion des données** : Sauvegarde/chargement JSON
- **Logique de matching** : Algorithme de détection des matches
- **Système de swipe** : Gestion des likes/dislikes

#### `SwipeView`
- **Interface utilisateur** : Boutons interactifs Discord
- **Navigation automatique** : Enchainement des profils
- **Gestion des interactions** : Validation des permissions

### Structure des données

```python
profiles = {
    user_id: {
        "likes": set(),      # IDs des personnes likées
        "dislikes": set(),   # IDs des personnes passées
        "active": bool       # Profil visible ou non
    }
}

matches = {
    user_id: set()  # IDs des matches mutuels
}
```

## 🔧 Configuration Avancée

### Personnalisation du préfixe
```python
bot = commands.Bot(command_prefix='!', intents=intents)
# Changez '!' par le préfixe souhaité
```

### Modification du timeout des boutons
```python
super().__init__(timeout=300)  # 5 minutes
# Ajustez la valeur en secondes
```

### Couleurs des embeds
```python
color=0xFF1493  # Rose pour le swipe
color=0xFF69B4  # Rose pour les matches
color=0x9932CC  # Violet pour les profils
```

## 📊 Fonctionnalités Techniques

- **Persistance des données** : Sauvegarde automatique en JSON
- **Gestion d'erreurs** : Try/catch pour la robustesse
- **Filtrage intelligent** : Évite les doublons et les bots
- **Interface responsive** : Boutons avec validation des permissions
- **Notifications publiques** : Annonces de matches avec @everyone

## 🛡️ Sécurité

- Validation des permissions utilisateur
- Protection contre les interactions non autorisées  
- Gestion des timeouts pour éviter les boutons morts
- Filtrage automatique des bots

## 📁 Fichiers Générés

- `tinder_data.json` : Stockage des profils et matches
- Structure automatiquement créée au premier lancement

## ⚠️ Notes Importantes

1. **Token de sécurité** : Ne partagez jamais votre token de bot
2. **Données sensibles** : Le fichier JSON contient les interactions des utilisateurs
3. **Permissions** : Assurez-vous que le bot a accès aux membres du serveur
4. **Modération** : Les admins peuvent reset les profils si nécessaire

## 🔄 Améliorations Possibles

- Système de photos de profil personnalisées
- Filtres avancés (âge, rôles, etc.)
- Messages privés automatiques lors des matches
- Statistiques globales du serveur
- Cooldowns entre les swipes
- Système de super-likes limités

---

*Créé avec ❤️ pour Discord | Utilisez de manière responsable*
