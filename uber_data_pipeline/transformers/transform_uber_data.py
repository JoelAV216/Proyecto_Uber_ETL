import pandas as pd
from datetime import datetime

if 'transformer' not in globals():
    from mage_ai.data_preparation.decorators import transformer

@transformer
def transform(data: pd.DataFrame, *args, **kwargs) -> dict:
    # --- DIAGNÓSTICO ---
    print("=== COLUMNAS DISPONIBLES ===")
    print(data.columns.tolist())
    print("=============================\n")
    
    # 1. Limpiar nombres de columnas
    data.columns = data.columns.str.strip()
    
    # 2. Verificar que las columnas requeridas existen
    required_cols = ['tpep_pickup_datetime', 'tpep_dropoff_datetime', 'passenger_count', 
                     'trip_distance', 'RatecodeID', 'payment_type']
    
    for col in required_cols:
        if col not in data.columns:
            print(f" ERROR: La columna '{col}' no existe en el DataFrame")
            print(f"Columnas disponibles: {data.columns.tolist()}")
            raise ValueError(f"Columna faltante: {col}")
    
    # 3. Limpiar datos nulos
    data = data.dropna(subset=required_cols)
    print(f" Filas después de limpiar nulos: {len(data)}")
    
    # 4. Convertir columnas de fecha/hora
    data['tpep_pickup_datetime'] = pd.to_datetime(data['tpep_pickup_datetime'], errors='coerce')
    data['tpep_dropoff_datetime'] = pd.to_datetime(data['tpep_dropoff_datetime'], errors='coerce')
    
    # 5. Eliminar filas con fechas inválidas
    data = data.dropna(subset=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
    
    # 6. Crear dim_datetime
    datetime_dim = data[['tpep_pickup_datetime', 'tpep_dropoff_datetime']].drop_duplicates().reset_index(drop=True)
    datetime_dim['pick_hour'] = datetime_dim['tpep_pickup_datetime'].dt.hour
    datetime_dim['pick_day'] = datetime_dim['tpep_pickup_datetime'].dt.day
    datetime_dim['pick_month'] = datetime_dim['tpep_pickup_datetime'].dt.month
    datetime_dim['pick_year'] = datetime_dim['tpep_pickup_datetime'].dt.year
    datetime_dim['pick_weekday'] = datetime_dim['tpep_pickup_datetime'].dt.weekday
    datetime_dim['datetime_id'] = datetime_dim.index
    
    # 7. Crear dim_passenger_count
    passenger_count_dim = data[['passenger_count']].drop_duplicates().reset_index(drop=True)
    passenger_count_dim['passenger_count_id'] = passenger_count_dim.index
    
    # 8. Crear dim_trip_distance
    trip_distance_dim = data[['trip_distance']].drop_duplicates().reset_index(drop=True)
    trip_distance_dim['trip_distance_id'] = trip_distance_dim.index
    
    # 9. Crear dim_rate_code
    rate_code_type = {
        1: 'Standard rate', 2: 'JFK', 3: 'Newark', 4: 'Nassau or Westchester',
        5: 'Negotiated fare', 6: 'Group ride'
    }
    rate_code_dim = data[['RatecodeID']].drop_duplicates().reset_index(drop=True)
    rate_code_dim['rate_code_name'] = rate_code_dim['RatecodeID'].map(rate_code_type)
    rate_code_dim['rate_code_id'] = rate_code_dim.index
    
    # 10. Crear dim_payment_type
    payment_type_name = {
        1: 'Credit card', 2: 'Cash', 3: 'No charge', 4: 'Dispute',
        5: 'Unknown', 6: 'Voided trip'
    }
    payment_type_dim = data[['payment_type']].drop_duplicates().reset_index(drop=True)
    payment_type_dim['payment_type_name'] = payment_type_dim['payment_type'].map(payment_type_name)
    payment_type_dim['payment_type_id'] = payment_type_dim.index
    
    # 11. Verificar si existen columnas de coordenadas
    has_coords = 'pickup_longitude' in data.columns and 'pickup_latitude' in data.columns
    
    if has_coords:
        # Crear dimensiones con coordenadas
        pickup_location_dim = data[['pickup_longitude', 'pickup_latitude']].drop_duplicates().reset_index(drop=True)
        pickup_location_dim['pickup_location_id'] = pickup_location_dim.index
        
        dropoff_location_dim = data[['dropoff_longitude', 'dropoff_latitude']].drop_duplicates().reset_index(drop=True)
        dropoff_location_dim['dropoff_location_id'] = dropoff_location_dim.index
        
        # Crear fact_table con coordenadas - USANDO PARÉNTESIS en lugar de \
        fact_table = (data.merge(datetime_dim, on=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
                         .merge(passenger_count_dim, on='passenger_count')
                         .merge(trip_distance_dim, on='trip_distance')
                         .merge(rate_code_dim, on='RatecodeID')
                         .merge(payment_type_dim, on='payment_type')
                         .merge(pickup_location_dim, on=['pickup_longitude', 'pickup_latitude'])
                         .merge(dropoff_location_dim, on=['dropoff_longitude', 'dropoff_latitude']))
    else:
        # Si no hay coordenadas, crear location_id simple
        print(" No se encontraron columnas de coordenadas, usando IDs numéricos")
        
        # Crear pickup_location_dim simple
        pickup_location_dim = pd.DataFrame({'pickup_location_id': [0]})
        
        # Crear dropoff_location_dim simple
        dropoff_location_dim = pd.DataFrame({'dropoff_location_id': [0]})
        
        # Crear fact_table sin coordenadas - USANDO PARÉNTESIS en lugar de \
        fact_table = (data.merge(datetime_dim, on=['tpep_pickup_datetime', 'tpep_dropoff_datetime'])
                         .merge(passenger_count_dim, on='passenger_count')
                         .merge(trip_distance_dim, on='trip_distance')
                         .merge(rate_code_dim, on='RatecodeID')
                         .merge(payment_type_dim, on='payment_type'))
        
        # Agregar columnas de location_id con valor 0
        fact_table['pickup_location_id'] = 0
        fact_table['dropoff_location_id'] = 0
    
    # Seleccionar columnas para fact_table
    fact_cols = ['datetime_id', 'passenger_count_id', 'trip_distance_id', 
                 'rate_code_id', 'payment_type_id', 'pickup_location_id', 
                 'dropoff_location_id']
    
    # Agregar otras columnas si existen
    for col in ['VendorID', 'store_and_fwd_flag', 'fare_amount', 'extra', 
                'mta_tax', 'tip_amount', 'tolls_amount', 'improvement_surcharge', 
                'total_amount']:
        if col in data.columns:
            fact_cols.append(col)
    
    fact_table = fact_table[fact_cols]
    
    print(f" Transformación completada. Filas en fact_table: {len(fact_table)}")
    
    return {
        'datetime_dim': datetime_dim,
        'passenger_count_dim': passenger_count_dim,
        'trip_distance_dim': trip_distance_dim,
        'rate_code_dim': rate_code_dim,
        'payment_type_dim': payment_type_dim,
        'pickup_location_dim': pickup_location_dim,
        'dropoff_location_dim': dropoff_location_dim,
        'fact_table': fact_table
    }