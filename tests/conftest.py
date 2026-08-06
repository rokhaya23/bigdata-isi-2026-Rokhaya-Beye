import os
import sys
import pytest
from pyspark.sql import SparkSession

# Forcer Spark à utiliser le Python de l'environnement virtuel actif
os.environ["PYSPARK_PYTHON"] = sys.executable
os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable

@pytest.fixture(scope="session")
def spark():
    return (
        SparkSession.builder
        .master("local[1]")
        .appName("TP-BigData-Tests")
        .getOrCreate()
    )

@pytest.fixture(scope="session")
def spark():
    """Fixture PySpark réutilisable pour la session de test."""
    session = (
        SparkSession.builder
        .master("local[2]")
        .appName("TP3-Tests")
        .getOrCreate()
    )
    yield session
    session.stop()