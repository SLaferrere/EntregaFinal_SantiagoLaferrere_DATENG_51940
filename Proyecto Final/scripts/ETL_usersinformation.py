import json
import os
import smtplib
import sys
from datetime import datetime

import psycopg2
import requests
from airflow.models import Variable
from dotenv import load_dotenv
from pyspark.sql import SparkSession
from pyspark.sql.functions import concat_ws
from pyspark.sql.functions import lit

# Carga de los datos del archivo .env
load_dotenv()


# Crea una session en Spark
def create_spark_session():
    os.environ["PYSPARK_PYTHON"] = sys.executable
    os.environ["PYSPARK_DRIVER_PYTHON"] = sys.executable
    """Se requiere un archivo .env con el path al driver que se encuentra en la carpeta DriverJDBC
    con el siguiente formato
    DRIVER_PATH= path"""
    spark = (
        SparkSession.builder.master("local")
        .appName("Conexion entre Pyspark y Amazon Redshift")
        .config("spark.jars", os.getenv("DRIVER_PATH"))
        .getOrCreate()
    )
    return spark


# Pega a la API y genera un DataFrame con los datos que nos interesa; elimina posibles duplicados y en caso de localizar menores de edad rompe y envia un mail avisandonos del error
def get_data():
    request = requests.get(
        "https://randomuser.me/api/?results=100&nat=au,gb,ie,nz,us"
    ).json()
    col_names = [
        "cellphone",
        "prefix",
        "full_name",
        "email",
        "age",
        "date_of_birth",
        "nationality",
    ]
    temp = (
        create_spark_session()
        .createDataFrame(request["results"])
        .select(
            "cell",
            "name.title",
            concat_ws(" ", "name.first", "name.last"),
            "email",
            "dob.age",
            "dob.date",
            "nat",
        )
        .dropDuplicates()
    )

    df = temp.toDF(*col_names)

    execution_date = (
        json.loads(os.getenv("process_date").replace("'", '"'))["process_date"]
        if os.getenv("process_date") != "{}"
        else datetime.now().strftime("%Y-%m-%d")
    )

    """Creadcion de DataFrame temporal donde
    se insertan, en caso de haber, la informacion
    de todos los menores de edad encontrados"""
    age_check = (
        df.select("full_name", "age")
        .where(df.age < Variable.get("UNDERAGE"))
        .rdd.flatMap(lambda x: x)
        .collect()
    )
    """Envia un mail con dicha informacion"""
    if age_check:
        msg = f"Subject: Error en la carga del {execution_date} - UsersInformation Table\n\nMenor de edad detectado: \n"
        msg += "".join(
            [
                f"\tNombre: {age_check[i]} edad: {age_check[i+1]}\n"
                for i in range(0, len(age_check), 2)
            ]
        )
        x = smtplib.SMTP("smtp.gmail.com", 587)
        x.starttls()
        x.login(Variable.get("SMTP_EMAIL_FROM"), Variable.get("SMTP_PASSWORD"))
        x.sendmail(Variable.get("SMTP_EMAIL_FROM"), Variable.get("SMTP_EMAIL_TO"), msg)
        raise Exception("ERROR")
    """En caso de no encontrar menores de edad
    nos devuelve el DataFrame final con una columna
    con la fecha del proceso"""
    df = df.withColumn("load_date", lit(execution_date))
    return df


# Crea un conector entre psycopg2 y RedShift
def connector():
    """Se requiere un archivo .env para poder cargar las credecinales de RedShift
    este tiene el sieguiente formato
    HOST = host de redshift.amazonaws.com
    PORT = numero de puerto
    DATABASE = database
    USER = usuario
    PASSWORD = contraseña"""
    conn = psycopg2.connect(
        host=os.getenv("HOST"),
        port=int(os.getenv("PORT")),
        database=os.getenv("DATABASE"),
        user=os.getenv("USER"),
        password=os.getenv("PASSWORD"),
    )
    conn.autocommit = True
    return conn


# Inserta el DataFrame en una tabla en RedShift
def main():
    df = get_data()
    conn = connector()

    with conn.cursor() as cur:
        (
            df.write.format("jdbc")
            .option(
                "url",
                f"jdbc:redshift://{os.getenv('HOST')}:{int(os.getenv('PORT'))}/{os.getenv('DATABASE')}",
            )
            .option("dbtable", "laferreresantiago_coderhouse.UsersInformation")
            .option("user", os.getenv("USER"))
            .option("password", os.getenv("PASSWORD"))
            .option("driver", "com.amazon.redshift.jdbc42.Driver")
            .mode("append")
            .save()
        )


if __name__ == "__main__":
    main()
