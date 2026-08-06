# Diagnostic technique — Les limites du traitement local

> **Livrable de la séance 1** — Big Data Engineering — UCAD
> Auteur : <Prénom NOM> — Date : <JJ/MM/AAAA>
> Longueur attendue : 1 à 2 pages. Toute affirmation doit s'appuyer sur une
> **mesure** issue de votre notebook (`notebooks/TP1_exploration.ipynb`).

## 1. Constats — où le traitement local atteint-il ses limites ?

Rapportez vos mesures (échelle 0.1 en local, échelle 1.0 sur Colab) :

| Opération | Échelle | Lignes | Temps (s) | Mémoire (Mo) | Observation |
|---|---|---|---|---|---|
| Chargement `orders.csv` | 0.1 | | | | |
| Jointure orders × items | 0.1 | | | | |
| Chargement `events.json` | 0.1 | | | | |
| Chargement `events.json` | 1.0 | | | | chargé / averti / crash ? |

Points à couvrir :
- le ratio mémoire / taille disque constaté, et son explication ;
- ce qui s'est passé (précisément) lors du chargement de `events.json` à
  l'échelle 1.0 ;
- l'extrapolation à 50 Go puis 1 To (hypothèse linéaire — dites pourquoi
  elle est optimiste ou pessimiste).

## 2. Analyse — pourquoi ça casse ?

Expliquez, avec vos mots et vos chiffres :
- pourquoi un DataFrame Pandas occupe plus de mémoire que le fichier source ;
- pourquoi la jointure aggrave le problème (pic mémoire, duplication) ;
- en quoi le *scale-up* (acheter plus de RAM) n'est pas une stratégie
  durable (coût, plafond, panne, croissance des données, concurrence
  d'accès) ;
- quelles parades locales existent (chunks, dtypes optimisés, formats
  binaires, échantillonnage) et **jusqu'où** elles repoussent le mur.

## 3. Besoins — ce qu'une architecture distribuée doit apporter

Formulez 4 à 6 exigences précises, par exemple sous la forme
« le système doit … ». Pistes : traiter des données plus grandes que la RAM
d'une machine ; paralléliser sur plusieurs machines ; tolérer la panne d'un
nœud ; lire des formats variés (CSV, JSON, …) ; rester pilotable depuis
Python ; passer à l'échelle sans réécrire le code.

Terminez par une phrase sur ce que Pandas **reste** le bon outil pour faire.

## 4. (Optionnel) Questions ouvertes

Ce que vous n'avez pas compris ou aimeriez approfondir — discuté en séance 2.
