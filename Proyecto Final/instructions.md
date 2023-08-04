# Proyecto Final
Proyecto Final de Coderhouse de Data Engineer Flex.

# Distribución de los archivos
Los archivos a tener en cuenta son:
* `docker_images/`: Contiene los Dockerfiles para crear las imagenes utilizadas de Airflow y Spark.
* `docker-compose.yml`: Archivo de configuración de Docker Compose. Contiene la configuración de los servicios de Airflow y Spark.
* `.env`: Archivo de variables de entorno. Contiene variables de conexión a Redshift y driver de Postgres. (Incluido en el .gitignore)
* `dags/`: Carpeta con los archivos de los DAGs.
    * `etl_users.py`: DAG principal que ejecuta el pipeline de extracción, transformación y carga de datos de usuarios.
* `logs/`: Carpeta con los archivos de logs de Airflow.
* `plugins/`: Carpeta con los plugins de Airflow.
* `postgres_data/`: Carpeta con los datos de Postgres.
* `scripts/`: Carpeta con los scripts de Spark.
    * `redshift-jdbc42-2.1.0.16.jar`: Driver de Redshift para Spark.
    * `create.sql`: Script de SQL para la creación de la tabla final.
    * `update.sql`: Script de SQL para la transformación de la tabla final.
    * `clean_load_date.sql`: Script de SQL para la eliminar las cargas del mismo dia.
    * `ETL_usersinformation.py`: Script de Spark que ejecuta el ETL.

# Pasos para ejecutar el Entregable 3
1. Posicionarse en la carpeta `Proyecto Final`. A esta altura debería ver el archivo `docker-compose.yml`.

2. Crear las siguientes carpetas a la misma altura del `docker-compose.yml`.
```bash
mkdir -p dags,logs,plugins,postgres_data,scripts
```

3. Crear un archivo con variables de entorno llamado `.env` ubicado a la misma altura que el `docker-compose.yml`. Cuyo contenido sea:
```bash
HOST=..
PORT=5439
DATABASE=...
USER=...
PASSWORD=...
DRIVER_PATH=/tmp/drivers/redshift-jdbc42-2.1.0.16.jar
```

4. Hacer el build de las imagenes que se encuentran en `Proyecto Final/docker_images/airflow` y `Proyecto Final/docker_images/spark`. Los comandos de ejecución se
encuentran en los mismos Dockerfiles.

5. Ejecutar el siguiente comando para levantar los servicios de Airflow y Spark.
```bash
docker-compose up --build
```
6. Una vez que los servicios estén levantados, ingresar a Airflow en `http://localhost:8080/`.

7. En la pestaña `Admin -> Connections` crear una nueva conexión con los siguientes datos para Redshift:
    * Conn Id: `redshift_default`
    * Conn Type: `Amazon Redshift`
    * Host: `host de redshift`
    * Database: `base de datos de redshift`
    * User: `usuario de redshift`
    * Password: `contraseña de redshift`
    * Port: `5439`

8. En la pestaña `Admin -> Connections` crear una nueva conexión con los siguientes datos para Spark:
    * Conn Id: `spark_default`
    * Conn Type: `Spark`
    * Host: `spark://spark`
    * Port: `7077`
    * Extra: `{"queue": "default"}`

9. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `DRIVER_CLASS_PATH`
    * Value: `/tmp/drivers/redshift-jdbc42-2.1.0.16.jar`

10. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `SPARK_SCRIPTS_DIR   `
    * Value: `/opt/airflow/scripts`

11. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `SMTP_EMAIL_FROM`
    * Value: `Email del cual queremos enviar las notificaciones`

12. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `SMTP_PASSWORD`
    * Value: `Contraseña requerida para enviar el mail`

13. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `SMTP_EMAIL_TO`
    * Value: `Mail al que queremos recibir las notificaciones`

14. En la pestaña `Admin -> Variables` crear una nueva variable con los siguientes datos:
    * Key: `UNDERAGE`
    * Value: `Edad a la cual consideramos menores de edad`
        * La API usada no genera registros de personas con 21 años o menos, por lo que para los fines practicos, esta deberia ser seteada en 20 para no "romper" y 25 para "romper".
          En caso de recibir una notificacion:
             ![alt text](https://github.com/SLaferrere/EntregaFinal_SantiagoLaferrere_DATENG_51940/blob/main/Proyecto%20Final/imagenes/Email%20.png)
         
15. Ejecutar el DAG `etl_users`.
