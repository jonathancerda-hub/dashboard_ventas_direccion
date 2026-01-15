import os
from dotenv import load_dotenv
from supabase import create_client
from collections import Counter

# Cargar variables de entorno
load_dotenv()

# Configuración de Supabase
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_KEY')

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

print("🔍 Explorando datos de Supabase para diciembre 2025...")

# Obtener datos de diciembre 2025
response = supabase.table('sales_lines').select('*').gte('invoice_date', '2025-12-01').lte('invoice_date', '2025-12-31').limit(100).execute()

if response.data:
    print(f"\n📊 Total registros encontrados: {len(response.data)}")
    
    # Mostrar primer registro completo para ver todos los campos
    print("\n📝 Estructura del primer registro:")
    first = response.data[0]
    for key, value in first.items():
        print(f"  - {key}: {value}")
    
    # Analizar campos relacionados con canal/grupo
    print("\n🔍 Análisis de campos clave:")
    
    campos_canal = ['canal', 'sales_channel_id', 'partner_group', 'customer_group', 'grupo_venta']
    
    for campo in campos_canal:
        if campo in first:
            valores = [r.get(campo) for r in response.data if r.get(campo)]
            contador = Counter(valores)
            print(f"\n  📌 Campo '{campo}':")
            for valor, count in contador.most_common(10):
                print(f"    - {valor}: {count} registros")
        else:
            print(f"\n  ⚠️ Campo '{campo}' no encontrado")
    
    # Buscar campos que contengan "group", "canal" o "team"
    print("\n\n🔎 Campos que contienen 'group', 'canal' o 'team':")
    for key in first.keys():
        if 'group' in key.lower() or 'canal' in key.lower() or 'team' in key.lower() or 'channel' in key.lower():
            print(f"  - {key}")
    
else:
    print("❌ No se encontraron datos")
