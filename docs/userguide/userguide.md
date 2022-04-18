# Conception OS - Guide d'utilisation

Afin de simplifier la correction du TP, nous vous offrons ce guide d'utilisation détaillé qui comporte deux parties.

- Création de la machine virtuelle Gentoo, téléchargement et démarrage de l'ISO d'installation
- Génération et execution du script d'installation

Toutes les étapes que vous voyez ici se retrouvent également sur la vidéo de démonstration.

## Création de la machine virtuelle

- Créer une machine virtuelle
    - CPU 64 bits (mettre le nombre maximum de cores)
    - Boot en mode BIOS (par défaut sur VirtualBox)
    - 4GB de RAM au moins (sauf si vous aimez attendre, de plus on a pas testé moins)
    - Un unique disque de 64GB
- Télécharger l'ISO d'installation minimale de Gentoo
    - https://www.gentoo.org/downloads/
    - "Minimal Installation CD" dans la section am64 (par défaut)
- Démarrer la machine virtuelle
    - Appuyer sur `enter` au menu de boot
    - Lorsque la machine vous demande un clavier, tapez `sf` (Swiss French), ou alors si vous l'avez manqué tapez `loadkeys fr_CH`.w
    - Si le démarrage se coince sur l'init syslog-ng appuyer sur `CTRL+C` et `enter` quelques fois (redémarrer si c'est toujours coincé et faire la manipulation immédiatement une fois arrivé sur syslog-ng). C'est possible de devoir spammer cette combinaison plusieurs fois avant que ça marche. Aucune idée de pourquoi ça fait ça nous n'avions jamais eu ça auparavent.

## Génération du script d'installation

Toute cette section est donnée à titre d'indication. Afin de vous faciliter la vie une archive du script d'installation toute prête est disponible à l'adresse [`https://github.com/frostblue/gentoo-installer/raw/main/dist/install.tar.gz`](https://github.com/frostblue/gentoo-installer/raw/main/dist/install.tar.gz)

- Cloner le projet
    - https://github.com/frostblue/gentoo-installer
- Si pas déjà présent, installer Python3
    - Installer via pip les paquets présents dans `requirements.txt`
    (possibilité pour cette étape d'tuliser le module venv de python)
    - Si lancé depuis linux il est possible de devoir aussi installer Qt5 (voir ses paquets en version dev) manuellement
- Lancer le script `guiconfig_geninstall.sh`
    - Dans **Localisation**
        - Changer la Time Zone
    - Dans **Partitions**
        - Taille de 65000 MiB
        - Drive : `/dev/sda`
        - Label `gpt`
        - Ajouter 3 partitions (laisser vide les champs non spécifiés ici; les noms des partitions ne sont pas importants mais doivent être présents)
            - Partition 1
                - Name : `bios`
                - Size : 2 MiB
                - Bootable : Yes
                - BiosBoot : Yes
            - Partition 2
                - Name : `boot`
                - Size : 1024 MiB
                - Bootable : Yes
                - Filesystem : `ext4`
                - Mountpoint : `/boot`
            - Partitions 3
                - Name : `root`
                - Filesystem : `ext4`
                - Mountpoint : `/`
    - Dans **Mirroirs**
        - Sélectionner un serveur parmis ceux proposés (récupérés dynamiquement via l'API Gentoo, idéalement séléctionner celui en Suisse)
        - Ne pas oublier de séléctionner l'URL dans la liste du bas (les liens `rsync` n'ont pas été testés, privilégier `https`).
    - Dans **System**
        - Mettre un hostname au choix
- Appuyer sur le bouton `Export` en bas à gauche
    - Une fois que le programme se ferme le script génère automatiquement un fichier `install.tar.gz` qui contient tout ce qu'il faut pour l'installation$
- Déplacer ce fichier quelque part de façon à pouvoir le récupérer plus tard
    - Idéalement le mettre sur le réseau (local ou non) de façon à pouvoir le `wget` depuis la machine virtuelle (ou l'ordinateur lui-même en cas d'installation sur une vraie machine).

## Installation de la machine virtuelle

Une fois le script d'installation généré il suffit de le copier sur la machine virtuelle

```shell=
mkdir installer
wget https://github.com/frostblue/gentoo-installer/raw/main/dist/install.tar.gz
tar xfv install.tar.gz
```

On peut ensuite se rendre dans le dossier `autogen`, lancer `install.sh` et aller se boire un petit café et revenir dans une heure.

```shell=
cd autogen
./install.sh
```
Si tout s'est bien passé vous devriez avoir ça sur votre écran

![](https://i.imgur.com/nJBwmrI.png)

Il vous suffira par la suite d'éteindre la machine virtuelle, enlever l'ISO d'installation et la redémarrer et voilà, une installation très basique de Gentoo!

Pour vous connecter il suffit de mettre `root` comme nom d'utilisateur, qui n'ayant pas de mot de passe pourra se connecter immédiatement. Notez que pour le moment le layout du clavier est redevenu celui américain, il suffit pour que le changement soit permanent d'éditer le fichier `/etc/conf.d/keymaps`, ou de simplement inclure le fichier de configuration déjà modifié dans le dossier `etc` du projet dont le contenu est automatiquement copié sur la machine pendant l'installation
