from pyspark.sql import DataFrame, functions as F

def unifier_manquants(df: DataFrame) -> DataFrame:
    """Remplace les chaînes vides ("") et "N/A" par null dans la colonne email."""
    return df.withColumn(
        "email",
        F.when(F.col("email").isin("", "N/A"), None).otherwise(F.col("email"))
    )

def normaliser_email(df: DataFrame) -> DataFrame:
    """Met l'email en minuscules, supprime les espaces et ajoute un drapeau email_valide."""
    df_clean = df.withColumn("email", F.trim(F.lower(F.col("email"))))
    regex_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
    return df_clean.withColumn(
        "email_valide",
        F.when(F.col("email").isNull(), False)
         .otherwise(F.col("email").rlike(regex_email))
    )

def normaliser_ville(df: DataFrame) -> DataFrame:
    """ville (affichage) + ville_norm (clé sans accent native)."""
    # 1. Formatage d'affichage
    df_clean = df.withColumn("ville", F.initcap(F.trim(F.col("ville"))))
    
    # 2. Suppression des accents nativement (sans UDF)
    accents   = "àáâãäåèéêëìíîïòóôõöùúûüýÿçÑñ"
    sans_acc  = "aaaaaaeeeeiiiiooooouuuuyycNn"
    
    return df_clean.withColumn(
        "ville_norm",
        F.lower(F.translate(F.col("ville"), accents, sans_acc))
    )


def normaliser_telephone(df):
    # 1. Nettoyer les espaces, le signe +, les tirets et points
    df_clean = df.withColumn(
        "tel_clean", 
        F.regexp_replace(F.col("telephone"), r"[\s\+\-\.]", "")
    )
    
    # 2. Si le numéro commence par '221' et fait 12 chiffres, retirer '221' (index PySpark commence à 1)
    df_clean = df_clean.withColumn(
        "tel_clean",
        F.when(
            (F.length(F.col("tel_clean")) == 12) & F.col("tel_clean").startswith("221"),
            F.expr("substring(tel_clean, 4, 9)")
        ).otherwise(F.col("tel_clean"))
    )
    
    # 3. Vérifier que les 9 chiffres restants correspondent à un mobile (70, 75, 76, 77, 78)
    return df_clean.withColumn(
        "telephone_valide",
        F.col("tel_clean").rlike(r"^(70|75|76|77|78)\d{7}$")
    )
def valider_naissance(df: DataFrame) -> DataFrame:
    """Valide la date de naissance entre 1920 et la date actuelle."""
    annee_naissance = F.year(F.to_date(F.col("date_naissance")))
    annee_courante = F.year(F.current_date())
    
    est_valide = (annee_naissance >= 1920) & (annee_naissance <= annee_courante)
    
    return df.withColumn(
        "date_naissance_valide",
        F.when(F.col("date_naissance").isNull(), False).otherwise(est_valide)
    )

def dedupliquer_clients(df: DataFrame) -> DataFrame:
    """Supprime les doublons après normalisation sur customer_id ou email."""
    return df.dropDuplicates(["email"])

def nettoyer_clients(df: DataFrame) -> DataFrame:
    """Pipeline complet de nettoyage des données clients."""
    return (
        df.transform(unifier_manquants)
          .transform(normaliser_email)
          .transform(normaliser_ville)
          .transform(normaliser_telephone)
          .transform(valider_naissance)
          .transform(dedupliquer_clients)
    )