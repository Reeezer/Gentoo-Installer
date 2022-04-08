# Gentoo Installer

## Introduction

Gentoo est une distribution Linux dont le gestionnaire de paquet (portage) installe les paquets à partir de leur code source. Gentoo est donc ce que l'on appelle une *source based distribution*, ce qui la rend plus configurable que n'importe quelle autre distribution basée sur des paquets binaires puisqu'il est possible de modifier les fonctionnalités des paquets avant leur compilation, par le biais d'un système de *USE-flags*

De par cette configurabilité, Gentoo est un système de paquets très flexible et très puissant, mais aussi complexe à configurer. De ce fait, l'installation du système doit se faire manuellement en ligne de commande puisqu'aucun installateur n'est fourni. Il est possible d'installer ce qu'on appelle des "stage4" qui sont des archives contenant un système complètement fonctionnel mais ceux-ci sont donc pré-configurés et non adaptés à une configuration plus spécifique.

C'est dans cette optique que nous avons décidé de créer un générateur de scripts d'installation, afin de pouvoir facilement décrire le système dans l'état final que l'on désire, et laisser le générateur créer le script avec les commandes dans le bon ordre afin d'installer le système à notre place. De cette façon il est facile de réinstaller le système plusieurs fois et de façon répétable sans devoir être derrière son écran. Il suffit de télécharger les scripts d'installation, lancer le principal, et revenir dans une heure ou deux une fois que le système a été compilé et installé.

## Structure du projet

Le projet est composé de deux parties, une partie qui se charge de générer un script d'installation, donnés des fichier de configuration, et une interface graphique qui permet de générer lesdits fichiers de configuration si l'on n'est pas à l'aise de les faire à la main.

## Fonctionnement des composants

### Générateur du script d'installation

