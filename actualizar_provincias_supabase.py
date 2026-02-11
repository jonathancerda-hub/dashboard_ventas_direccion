"""
Script para agregar información de provincia a los registros de Supabase
Obtiene estado/provincia desde Odoo basándose en partner_id
"""
import os
import sys
from dotenv import load_dotenv
from odoo_manager import OdooManager
from supabase_manager import SupabaseManager

load_dotenv()

# Verificar si se pasó --yes como argumento
auto_confirm = '--yes' in sys.argv or '-y' in sys.argv

print("🚀 Iniciando actualización de provincias en Supabase...")
print("=" * 80)

# Conectar a Odoo y Supabase
odoo_manager = OdooManager()
supabase_manager = SupabaseManager()

# Obtener lista de partner_ids únicos en Supabase 2025
print("\n📊 Paso 1: Obteniendo lista de clientes en Supabase...")
result = supabase_manager.supabase.table('ventas_odoo_2025')\
    .select('id, partner_id')\
    .execute()

if not result.data:
    print("❌ No se encontraron registros en Supabase")
    exit(1)

# Obtener partner_ids únicos
partner_ids = list(set([r['partner_id'] for r in result.data if r.get('partner_id')]))
print(f"✅ Encontrados {len(partner_ids)} clientes únicos")

# Obtener información de estado/provincia de Odoo
print("\n📊 Paso 2: Obteniendo información de estado/provincia desde Odoo...")
print(f"   Consultando {len(partner_ids)} partners...")

try:
    partners_data = odoo_manager.models.execute_kw(
        odoo_manager.db, odoo_manager.uid, odoo_manager.password,
        'res.partner', 'search_read',
        [[('id', 'in', partner_ids)]],
        {'fields': ['id', 'name', 'state_id', 'city']}
    )
    
    print(f"✅ Obtenidos {len(partners_data)} partners con información")
    
    # Crear diccionario de mapeo
    partner_state_map = {}
    for partner in partners_data:
        partner_id = partner['id']
        state_info = partner.get('state_id')
        city = partner.get('city')
        
        if state_info and isinstance(state_info, list) and len(state_info) > 1:
            partner_state_map[partner_id] = {
                'state_id': state_info[0],
                'state_name': state_info[1],
                'city': city or ''
            }
    
    print(f"✅ Mapeados {len(partner_state_map)} partners con estado/provincia")
    
    # Mostrar algunos ejemplos
    print("\n📋 Ejemplos de mapeo:")
    for i, (partner_id, info) in enumerate(list(partner_state_map.items())[:5]):
        print(f"   • Partner {partner_id}: {info['state_name']} - {info['city']}")
    
    # Confirmar antes de actualizar
    print(f"\n{'='*80}")
    print(f"📋 RESUMEN:")
    print(f"   • Registros en Supabase: {len(result.data)}")
    print(f"   • Partners únicos: {len(partner_ids)}")
    print(f"   • Partners con provincia: {len(partner_state_map)}")
    print(f"{'='*80}")
    
    if not auto_confirm:
        respuesta = input("\n⚠️ ¿Deseas agregar columnas state_id, state_name y city a Supabase? (SI/no): ")
        
        if respuesta.upper() != 'SI':
            print("\n❌ Operación cancelada")
            exit(0)
    else:
        print("\n✅ Modo auto-confirmación activado (--yes)\n")
    
    # NOTA: Para agregar columnas a Supabase, se debe hacer desde la interfaz web
    # o usando SQL directo. Este script mostrará el SQL necesario.
    print("\n" + "=" * 80)
    print("📝 INSTRUCCIONES:")
    print("=" * 80)
    print("\n1. Ve a https://supabase.com y abre tu proyecto")
    print("2. Ve a SQL Editor")
    print("3. Ejecuta el siguiente SQL:\n")
    
    sql = """
-- Agregar columnas para estado/provincia
ALTER TABLE ventas_odoo_2025 
ADD COLUMN IF NOT EXISTS state_id INTEGER,
ADD COLUMN IF NOT EXISTS state_name TEXT,
ADD COLUMN IF NOT EXISTS city TEXT;

-- Crear índice para mejorar performance
CREATE INDEX IF NOT EXISTS idx_ventas_2025_state ON ventas_odoo_2025(state_id);
"""
    print(sql)
    
    print("\n4. Después de ejecutar el SQL, vuelve a ejecutar este script para actualizar los datos")
    
    # Verificar si las columnas ya existen
    test_result = supabase_manager.supabase.table('ventas_odoo_2025')\
        .select('id, partner_id, state_id, state_name, city')\
        .limit(1)\
        .execute()
    
    if test_result.data and 'state_id' in test_result.data[0]:
        print("\n✅ Las columnas ya existen en Supabase")
        print("\n📊 Paso 3: Actualizando registros...")
        
        # Agrupar registros por partner_id para actualizar en lotes
        records_by_partner = {}
        for record in result.data:
            partner_id = record.get('partner_id')
            if partner_id:
                if partner_id not in records_by_partner:
                    records_by_partner[partner_id] = []
                records_by_partner[partner_id].append(record['id'])
        
        total_updated = 0
        total_partners = len(records_by_partner)
        
        for idx, (partner_id, record_ids) in enumerate(records_by_partner.items(), 1):
            if partner_id in partner_state_map:
                state_info = partner_state_map[partner_id]
                
                try:
                    # Actualizar todos los registros de este partner de una vez
                    supabase_manager.supabase.table('ventas_odoo_2025')\
                        .update({
                            'state_id': state_info['state_id'],
                            'state_name': state_info['state_name'],
                            'city': state_info['city']
                        })\
                        .in_('id', record_ids)\
                        .execute()
                    
                    total_updated += len(record_ids)
                    
                except Exception as e:
                    print(f"\n   ⚠️ Error actualizando partner {partner_id}: {e}")
            
            print(f"   📦 Procesados {idx}/{total_partners} partners ({total_updated} registros actualizados)", end='\r')
        
        print(f"\n\n✅ Actualización completada")
        print(f"   • Partners procesados: {total_partners}")
        print(f"   • Registros actualizados: {total_updated}")
        print(f"   • Registros sin provincia: {len(result.data) - total_updated}")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
