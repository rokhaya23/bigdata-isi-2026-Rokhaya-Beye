# 📊 Diagnostic qualité des données – customers.csv

## 🎯 Objectif
Mesurer les défauts présents dans le dataset AVANT nettoyage.

---

## 📋 Tableau des défauts

| Défaut | Mesure | Colonne | Décision |
|--------|--------|--------|----------|
| Emails manquants (null + "" + "N/A") | 150 | email | Uniformisation en null |
| Villes distinctes avant normalisation | 499 | ville | Normalisation (trim + initcap + suppression accents) |
| Noms avec espaces parasites | 100 | nom | Suppression des espaces avec trim |
| Dates de naissance hors bornes | 0 | date_naissance | Conversion en date + remplacement des valeurs invalides par null |
| Doublons exacts | 15 | toutes | Suppression |
| Téléphones non conformes | 3555 | telephone | Nettoyage + regex + flag de validité |

---

## 🧠 Analyse

- Le dataset contient plusieurs défauts de qualité pouvant fausser les analyses.
- Les valeurs manquantes d'email sont uniformisées en null. Les emails présents sont normalisés et une colonne de validité est ajoutée.
- Les villes peuvent contenir des variations de casse, d'espaces ou d'accents. Une normalisation est appliquée afin d'obtenir une clé homogène pour les analyses et les comparaisons.
- Les doublons peuvent provenir de répétitions d'enregistrements ou de différences de format dans les données.

---

## ⚙️ Choix de nettoyage

- Les différentes formes de valeurs manquantes dans les emails (`""`, `"N/A"`, `"NULL"`) sont converties en null. Les emails existants sont ensuite normalisés en minuscules et contrôlés avec un indicateur de validité.
- Les villes sont standardisées afin d'éviter les différences liées aux espaces, à la casse et aux accents.
- Les numéros de téléphone sont nettoyés pour conserver uniquement les chiffres, le préfixe pays `221` est supprimé et un contrôle de validité est ajouté selon le format sénégalais.
- Les dates de naissance sont converties au format date et les valeurs incohérentes sont remplacées par null.
- Les doublons sont traités après normalisation afin d'améliorer leur détection.

---

## 📌 Conclusion

Le nettoyage permet de garantir :
- des agrégations fiables ;
- une meilleure déduplication ;
- une réduction des incohérences de format ;
- une meilleure fiabilité des analyses.