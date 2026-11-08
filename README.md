#log_analysis :

##Objectif :Le but de ce projet est d’analyser les journaux de connexion SSH d’un serveur. Le serveur enregistre les tentatives de connexion dans des fichiers comme auth.log. Comme ces fichiers peuvent être très longs, le programme les lit automatiquement, repère les connexions réussies et échouées, puis résume les résultats dans des tableaux et des graphiques. Cela permet de comprendre plus facilement les tentatives d’accès au serveur.

##Structure de projet :
- ingestion/ : lit les fichiers de logs dans data/ et rassemble leurs lignes.
- processing/ : repère les tentatives SSH et récupère leurs informations : réussite ou échec, utilisateur et adresse IP.
- serving/ : compte les résultats et les présente dans des tableaux et des graphiques.
- main.py : lance le programme et appelle les différentes étapes dans l’ordre.

##Lancer le projet :
main.py est le point de départ du programme. Il prépare les logs, puis lance successivement :
1. la lecture des fichiers 
2. l’analyse des lignes 
3. la création des tableaux et graphiques.
uv run main.py

##Dashboard :
Les trois statistiques du dashboard
- Le nombre de tentatives échouées pour chaque pays.
- Le nombre de connexions réussies pour chaque utilisateur.
- Le nombre de tentatives échouées avec un utilisateur inexistant (invalid user), regroupées par nom d’utilisateur.

##Le fichier logging :
Le fichier s’appelle app.log. Il se trouve à la racine du projet, dans le dossier log_analysis, si le programme est configuré comme décrit. Il contient les messages produits pendant l’exécution : les fichiers lus, la création du dashboard et les problèmes rencontrés. Les messages sont classés par niveau : INFO, WARNING ou ERROR, et indiquent quel module les a écrits.
app.log, c’est un fichier où le programme note ce qui se passe pendant son exécution

##Remarque :
L’analyse a trouvé 10 962 tentatives échouées et seulement 1 connexion réussie. il y a donc beaucoup plus d’échecs que de réussites dans les fichiers analysés. Pour la statistique par pays, il faut associer chaque adresse IP à un pays. Si le programme ne trouve pas cette information, ou si certaines IP ne peuvent pas être localisées, le résultat par pays peut être incomplet ou afficher une catégorie inconnue

