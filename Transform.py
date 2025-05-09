import pandas as pd

# === PASO 1: CARGAR EL ARCHIVO CSV ===
# Reemplaza el nombre del archivo con el tuyo real
archivo = 'capufe_datos.csv'
df = pd.read_csv(archivo)

# === PASO 2: CONVERTIR MES A NÚMERO ===
meses = {
    'ENERO': 1, 'FEBRERO': 2, 'MARZO': 3, 'ABRIL': 4,
    'MAYO': 5, 'JUNIO': 6, 'JULIO': 7, 'AGOSTO': 8,
    'SEPTIEMBRE': 9, 'OCTUBRE': 10, 'NOVIEMBRE': 11, 'DICIEMBRE': 12
}
df['MES_NUM'] = df['MES'].map(meses)

# === PASO 3: CREAR COLUMNA DE FECHA ===
df['FECHA'] = pd.to_datetime(df['A—O'].astype(str) + '-' + df['MES_NUM'].astype(str) + '-01')

# === PASO 4: SELECCIONAR COLUMNAS DE VEHÍCULOS ===
columnas_vehiculos = [
    'AUTOS', 'MOTOS', 'AUTOBUS DE 2 EJES', 'AUTOBUS DE 3 EJES', 'AUTOBUS DE 4 EJES',  # Autobuses
    'CAMIONES DE 2 EJES', 'CAMIONES DE 3 EJES', 'CAMIONES DE 4 EJES', 'CAMIONES DE 5 EJES',  # Camiones
    'CAMIONES DE 6 EJES', 'CAMIONES DE 7 EJES', 'CAMIONES DE 8 EJES', 'CAMIONES DE 9 EJES', 'TRICICLOS'  # Camiones 
]

# === PASO 5: TRANSFORMAR A FORMATO LARGO ===
df_largo = df.melt(
    id_vars=['NOMBRE', 'FECHA'],
    value_vars=columnas_vehiculos,
    var_name='TIPO_VEHICULO',
    value_name='CONTEO'
)

# === PASO 6: LIMPIAR DATOS ===
df_largo = df_largo.dropna()
df_largo = df_largo[df_largo['CONTEO'] > 0]

# === PASO 7: VERIFICAR ===
print(df_largo.head())