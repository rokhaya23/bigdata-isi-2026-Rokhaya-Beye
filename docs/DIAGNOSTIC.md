# Diagnostic technique — Les limites du traitement local

> **Livrable de la séance 1** — Big Data Engineering — UCAD
> Auteur : <Prénom NOM> — Date : <JJ/MM/AAAA>
> Longueur attendue : 1 à 2 pages. Toute affirmation doit s'appuyer sur une
> **mesure** issue de votre notebook (`notebooks/TP1_exploration.ipynb`).

## 1. Constats — où le traitement local atteint-il ses limites ?

Rapportez vos mesures (échelle 0.1 en local, échelle 1.0 sur Colab) :

| Opération | Échelle | Lignes | Temps (s) | Mémoire (Mo) | Observation |
|---|---|---|---|---|---|
| Chargement `orders.csv` | 0.1 | 50 000 | 0.25 | 18.5 | disque : 3.3 Mo — ratio mém/disque ≈ 5.6x |
| Jointure orders × items | 0.1 | 112 750 | 0.11 | 56.3 | disque : n/a (résultat en mémoire uniquement) |
| Chargement `events.json` | 0.1 | 329 976 | 7.61 | 144.4 | disque : 68.5 Mo — ratio mém/disque ≈ 2.1x |
| Chargement `events.json` | 1.0 | 3 301 501 | 36.43 | 1 412.0 | disque : 685.0 Mo — chargé sans crash, ratio 2.1x, RAM système 6.1/12.7 Go |

Ratio mémoire / taille disque. Sur events.json, ce ratio est stable aux deux échelles (2.1x), ce qui suggère qu'il s'agit d'un comportement structurel de Pandas et non d'un artefact de volume. Il s'explique par le fait que les chaînes de caractères JSON, une fois chargées, deviennent des objets Python individuels (avec leur propre overhead mémoire), et que Pandas ajoute un index et des structures internes qui n'existent pas dans le fichier source.

Chargement de events.json à l'échelle 1.0. Le chargement complet (3,3 millions de lignes, 685 Mo sur disque) s'est déroulé sans crash sur Colab, en 36,43 s, en consommant 1 412 Mo de RAM — soit environ 6,1 Go sur les 12,7 Go disponibles sur l'instance Colab. On reste donc encore loin de la limite, mais l'écart entre la taille disque (685 Mo) et l'empreinte mémoire réelle (1 412 Mo, soit plus du double) montre que le mur se rapproche plus vite que ne le laisserait penser la seule taille des fichiers.

Extrapolation. Entre l'échelle 0.1 et l'échelle 1.0 (volume ×10), le temps de chargement n'a été multiplié que par 4,8 (7,61 s → 36,43 s) alors que la mémoire a été multipliée par 9,8 (144,4 Mo → 1 412 Mo), donc quasiment linéaire. Le temps semble donc croître un peu plus lentement que le volume (probablement grâce à un effet d'amortissement des coûts fixes de pd.read_json), tandis que la mémoire, elle, suit une croissance linéaire fidèle au volume de données.

L'hypothèse linéaire est plutôt optimiste : elle suppose que le ratio mémoire/disque reste constant à 2.1x indéfiniment, alors qu'en pratique, au-delà d'un certain volume, les mécanismes de gestion mémoire de Python (fragmentation, copies intermédiaires lors des opérations, swapping disque) dégradent les performances de façon plus que linéaire. Une extrapolation réaliste devrait donc plutôt anticiper un mur atteint avant les seuils indiqués ci-dessus.

## 2. Analyse — pourquoi ça casse ?

Pourquoi un DataFrame occupe plus de mémoire que le fichier source. Mes mesures le confirment directement : events.json pèse 68,5 Mo sur disque à l'échelle 0.1 mais occupe 144,4 Mo une fois chargé en mémoire (ratio 2,1x), et ce ratio reste identique à l'échelle 1.0. Le fichier JSON sur disque est une représentation texte compacte ; une fois parsé, chaque chaîne de caractères devient un objet Python à part entière (avec en-tête d'objet, référence, allocation mémoire indépendante), et Pandas ajoute par dessus un index et des structures de colonnes (dtype=object pour le texte, qui stocke des pointeurs vers ces objets plutôt que des valeurs compactes).

Pourquoi la jointure aggrave le problème. Ma mesure de la jointure orders × items à l'échelle 1.0 montre : mémoire avant fusion (orders + items séparément) = 395 Mo, mémoire du résultat seul = 564 Mo. Le résultat de la jointure occupe donc à lui seul plus que la somme des deux tables d'origine, car chaque ligne d'order_items se voit dupliquer toutes les colonnes de la commande correspondante (jointure one-to-many). De plus, pendant l'exécution du merge(), Pandas doit garder les deux DataFrames d'entrée et construire le DataFrame de sortie simultanément en mémoire avant de pouvoir libérer les entrées — d'où un pic mémoire pouvant atteindre 2 à 3x la taille des données utiles.

Pourquoi le scale-up n'est pas une stratégie durable. Acheter plus de RAM déplace le mur sans le supprimer : le coût d'une machine à très grande mémoire croît plus vite que linéairement avec sa capacité, il existe un plafond physique (une seule machine ne peut pas dépasser une certaine quantité de RAM), une panne matérielle sur cette machine unique interrompt tout le traitement (aucune redondance), et le volume de données réel (50 Go, 1 To) croît généralement plus vite que le budget matériel disponible. Enfin, une seule machine ne peut servir qu'un nombre limité d'utilisateurs ou de traitements concurrents.

Parades locales possibles et leurs limites.

Chunks (pd.read_csv(..., chunksize=...)) : permet de traiter les données par morceaux sans tout charger en mémoire, mais complique les opérations qui nécessitent une vue globale (tri, jointure complète, agrégations qui dépendent de l'ensemble des données).
Dtypes optimisés (category pour les chaînes répétées, int32 au lieu de int64, etc.) : peut réduire l'empreinte mémoire de 30 à 70 % selon les données, mais ne change pas l'ordre de grandeur du problème pour des volumes qui dépassent largement la RAM disponible.
Formats binaires (Parquet, Feather) : bien plus compacts et rapides à lire que CSV/JSON, réduisent la taille sur disque et le temps de chargement, mais n'éliminent pas la limite de RAM une fois les données décompressées en mémoire.
Échantillonnage : utile pour l'exploration et le prototypage, mais inadapté dès que l'exhaustivité des données est requise (comptabilité, audit, jointures complètes).

Ces techniques repoussent le mur d'un facteur limité (typiquement ×2 à ×10 selon la technique), mais ne changent pas fondamentalement l'échelle atteignable sur une seule machine : au-delà d'un certain volume (dans mon cas, quelque part entre les 685 Mo mesurés sans problème et les 50 Go projetés), elles ne suffisent plus.

## 3. Besoins — ce qu'une architecture distribuée doit apporter

Le système doit pouvoir traiter des volumes de données plus grands que la RAM d'une seule machine, en répartissant les données sur plusieurs nœuds plutôt qu'en les chargeant intégralement en mémoire centrale.
Le système doit paralléliser les calculs sur plusieurs machines simultanément, afin que le temps de traitement ne croisse pas linéairement (voire pire) avec le volume de données.
Le système doit tolérer la panne d'un nœud sans perdre le travail en cours ni les données, contrairement à une machine unique où toute panne interrompt entièrement le traitement.
Le système doit pouvoir lire des formats de données variés (CSV, JSON, Parquet, etc.) de façon native, sans étape de conversion manuelle préalable coûteuse.
Le système doit rester pilotable depuis Python (ou un langage similaire), afin de conserver la productivité et l'écosystème déjà maîtrisés (comme avec Pandas) plutôt que d'imposer un changement complet d'outillage.
Le système doit permettre de passer à l'échelle progressivement (ajouter des nœuds) sans réécrire la logique métier du code à chaque changement de volume.

Pandas reste néanmoins le bon outil pour l'exploration rapide, le prototypage et l'analyse de données de taille modeste (jusqu'à quelques centaines de Mo à quelques Go selon la RAM disponible) — les mesures de ce TP le confirment jusqu'à 685 Mo sans difficulté.

## 4. (Optionnel) Questions ouvertes

Ce que vous n'avez pas compris ou aimeriez approfondir — discuté en séance 2.
