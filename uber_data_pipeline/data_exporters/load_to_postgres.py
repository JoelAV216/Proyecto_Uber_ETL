from mage_ai.io.postgres import Postgres
from sqlalchemy import create_engine
import pandas as pd

if 'data_exporter' not in globals():
    from mage_ai.data_preparation.decorators import data_exporter

@data_exporter
def export_data_to_postgres(data: dict, **kwargs) -> None:
    # Obtener las credenciales de las variables de entorno
    user = 'postgres'
    password = 'postgres'
    host = 'postgres'
    port = '5432'
    database = 'uber_db'

    # Crear la conexión a PostgreSQL
    connection_string = f'postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}'
    engine = create_engine(connection_string)

    for table_name, df in data.items():
        print(f"Cargando tabla: {table_name}")
        df.to_sql(name=table_name, con=engine, if_exists='replace', index=False)
    print("Datos cargados exitosamente en PostgreSQL")