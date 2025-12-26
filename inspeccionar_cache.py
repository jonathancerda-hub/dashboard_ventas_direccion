import pickle
import os

# Cambia estos valores por el año y mes que quieras revisar
año = 2025
mes = 12

cache_dir = os.path.join(os.path.dirname(__file__), '__pycache__', 'dashboard_cache')
cache_file = os.path.join(cache_dir, f"{año}_{mes:02d}.pkl")

if not os.path.exists(cache_file):
    print(f"No existe el archivo de caché: {cache_file}")
else:
    with open(cache_file, 'rb') as f:
        data = pickle.load(f)
    print(f"Claves en el caché: {list(data.keys())}")
    tendencia = data.get('tendencia_12_meses', None)
    if tendencia is None:
        print("No se encontró la clave 'tendencia_12_meses' en el caché.")
    elif not tendencia:
        print("La clave 'tendencia_12_meses' está vacía.")
    else:
        print(f"Hay {len(tendencia)} registros en 'tendencia_12_meses'. Ejemplo:")
        print(tendencia[:2])
