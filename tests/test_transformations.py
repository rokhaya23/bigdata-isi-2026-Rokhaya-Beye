import pytest
from chispa import assert_df_equality
from pyspark.sql.types import StructType, StructField, StringType, BooleanType
from src.transformations import (
    unifier_manquants,
    normaliser_email,
    normaliser_ville,
    normaliser_telephone,
    dedupliquer_clients
)

def test_unifier_manquants(spark):
    source_data = [("N/A",), ("",), ("user@test.com",)]
    schema = StructType([StructField("email", StringType(), True)])
    df_source = spark.createDataFrame(source_data, schema)

    df_res = unifier_manquants(df_source)

    expected_data = [(None,), (None,), ("user@test.com",)]
    df_expected = spark.createDataFrame(expected_data, schema)

    assert_df_equality(df_res, df_expected)

def test_normaliser_ville(spark):
    source_data = [("C1", " Thiès "), ("C2", "THIES")]
    schema = ["customer_id", "ville"]
    df_source = spark.createDataFrame(source_data, schema)

    df_res = normaliser_ville(df_source)
    villes_norm = [r["ville_norm"] for r in df_res.select("ville_norm").collect()]

    # Doivent générer exactement la même clé normalisée
    assert villes_norm[0] == villes_norm[1] == "thies"

def test_normaliser_telephone(spark):
    source_data = [("+221 77 123 45 67",), ("77-123-45-67",), ("33 820 00 00",)]
    df_source = spark.createDataFrame(source_data, ["telephone"])

    df_res = normaliser_telephone(df_source)
    valides = [r["telephone_valide"] for r in df_res.select("telephone_valide").collect()]

    assert valides == [True, True, False]

def test_dedupliquer_clients(spark):
    source_data = [("test@ucad.sn",), ("TEST@UCAD.SN",)]
    df_source = spark.createDataFrame(source_data, ["email"])

    # Normalisation préalable imposée avant déduplication
    df_norm = normaliser_email(df_source)
    df_res = dedupliquer_clients(df_norm)

    assert df_res.count() == 1