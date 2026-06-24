# Proyecto de Ingeniería de Datos: Análisis de Viajes de Uber/NYC Taxi

## Descripción
Este proyecto implementa un pipeline ETL (Extracción, Transformación y Carga) de extremo a extremo para analizar datos de viajes de taxis en Nueva York. El pipeline orquesta la ingesta, transformación y carga de datos en una base de datos PostgreSQL, utilizando un modelo en estrella (star schema) optimizado para análisis de negocio.

## Tecnologías Utilizadas
- **Docker & Docker Compose**: Orquestación de contenedores.
- **Mage AI**: Orquestación y ejecución del pipeline ETL.
- **PostgreSQL**: Almacenamiento de datos y modelo dimensional.
- **pgAdmin**: Exploración y consulta de datos.
- **Python (Pandas, SQLAlchemy)**: Transformación y carga de datos.

## Modelo de Datos
El modelo sigue un esquema en estrella con:
- **7 Tablas de Dimensión**: datetime, passenger_count, trip_distance, rate_code, payment_type, pickup_location, dropoff_location.
- **1 Tabla de Hechos**: fact_table con métricas de viajes (total_amount, fare_amount, tip_amount, etc.).
