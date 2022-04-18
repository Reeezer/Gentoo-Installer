# TP03 Conception OS - Configuration et compilation automatique d'un système Gentoo

###### Participants : Tania Tripiciano, Luca Meyer, Léon Muller

## Cahier des charges

La compilation et configuration du système d'exploitation Gentoo est une opération longue et fastidieuse, il faut en général une semaine de libre pour pouvoir tout configurer à la main, tant les possibilités de personnalisation sont nombreuses.

Nous avons donc choisi de créer un programme permettant à un utilisateur de choisir via une interface graphique (ou directement en modifiant le fichier de configuration à la main) de choisir la personnalisation du système qu'il souhaite. Puis de compiler automatiquement, sur un noyau, le système d'exploitation Gentoo en fonction du fichier de configuration généré. Ainsi l'utilisateur n'aura besoin que de choisir les paramètres qu'il souhaite, de lancer la compilation, et de se faire couler un long café.