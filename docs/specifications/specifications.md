# Conception OS - Cahier des charges

# Participants

*Luca Meyer*
*Léon Muller*
*Tania Tripiciano*

# Introduction

Pour le projet du cours de conception OS, nous avons choisit de travailler avec la distribution Linux Gentoo, et de concevoir un installateur permettant de créer une configuration de la distribution, ainsi que de l'installer automatiquement.

En effet, cette distribution peut être entièrement configurée, ce qui la rend optimale sur n'importe quelle architecture hardware. Cependant, comme cette configuration est pointue, et spécifique à chaque machine, elle requiert un temps conséquent pour la créer et l'installer. De plus, cette distribution n'est dotée que d'un 'handbook' décrivant les différentes étapes et commandes de configuration et d'installation. C'est pourquoi nous avons décidé de réaliser un installateur et une interface graphique permettant la configuration de Gentoo.

## Objectifs

- Interface graphique permattant la configuration de la distribution
	- Lister les différents paramètres permettant la personnalisation de la configuration (Tania)
	- Permettre à un utilisateur de créer une configuration custom via une interface graphique (Tania)
	- Génération des fichiers de configuration à partir des choix de l'utilisateur (Léon)
- Installateur
	- Lister les différentes commandes et étapes à effectuer (Léon)
	- Création d'un script permettant d'exécuter toutes les étapes une à une et dans l'ordre (Luca)
	- Utilisation des fichiers de configuration générés pour personnaliser l'installation (Luca)
	- Si aucun fichier de configuration n'est fournit, utiliser une configuration par défaut (Luca)

## Objectifs secondaires

- LUKS
- LVM 
- initramfs