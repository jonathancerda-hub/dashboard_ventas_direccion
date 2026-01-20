"""
Script para agregar y actualizar el campo product_life_cycle en Supabase
Este script obtiene el ciclo de vida de los productos desde Odoo y actualiza la tabla sales_lines en Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from odoo_manager import OdooManager
from datetime import datetime

load_dotenv(override=True)

def main():
    print("🚀 Iniciando actualización de ciclo de vida de productos en Supabase...")
    
    # Conectar a Supabase
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_key = os.getenv('SUPABASE_KEY')
    
    if not supabase_url or not supabase_key:
        print("❌ Error: SUPABASE_URL o SUPABASE_KEY no están configuradas")
        return
    
    supabase: Client = create_client(supabase_url, supabase_key)
    print("✅ Conectado a Supabase")
    
    # Conectar a Odoo
    try:
        odoo = OdooManager()
        print("✅ Conectado a Odoo")
    except Exception as e:
        print(f"❌ Error conectando a Odoo: {e}")
        return
    
    # Obtener todos los productos únicos de la tabla sales_lines
    print("\n📦 Obteniendo productos únicos de Supabase...")
    try:
        product_ids = set()
        batch_size = 1000
        offset = 0
        
        print("   Escaneando todos los registros para encontrar productos únicos...")
        while True:
            result = supabase.table('sales_lines')\
                .select('product_id')\
                .range(offset, offset + batch_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            # Agregar IDs únicos
            for row in result.data:
                if row.get('product_id'):
                    product_ids.add(row['product_id'])
            
            offset += batch_size
            
            if offset % 10000 == 0:
                print(f"   Procesados {offset} registros, productos únicos encontrados: {len(product_ids)}")
            
            # Si obtuvimos menos que el tamaño de página, no hay más datos
            if len(result.data) < batch_size:
                break
        
        print(f"   📊 Total productos únicos encontrados: {len(product_ids)}")
        
        if not product_ids:
            print("⚠️ No se encontraron productos en Supabase")
            return
        
    except Exception as e:
        print(f"❌ Error obteniendo productos de Supabase: {e}")
        return
    
    # Obtener ciclo de vida de productos desde Odoo
    print("\n🔄 Obteniendo ciclo de vida de productos desde Odoo...")
    product_lifecycle = {}
    
    try:
        if product_ids:
            # Obtener productos en lotes para evitar timeout
            batch_size = 100
            product_list = list(product_ids)
            
            for i in range(0, len(product_list), batch_size):
                batch = product_list[i:i + batch_size]
                print(f"   Procesando lote {i//batch_size + 1}/{(len(product_list) + batch_size - 1)//batch_size}...")
                
                # Obtener product.product con el campo product_life_cycle directamente
                products = odoo.models.execute_kw(
                    odoo.db, odoo.uid, odoo.password,
                    'product.product', 'read',
                    [batch],
                    {'fields': ['id', 'product_life_cycle']}
                )
                
                # Mapear product_id -> lifecycle
                for product in products:
                    product_lifecycle[product['id']] = product.get('product_life_cycle', 'No definido')
        
        print(f"   ✅ Ciclo de vida obtenido para {len(product_lifecycle)} productos")
        
    except Exception as e:
        print(f"❌ Error obteniendo ciclo de vida desde Odoo: {e}")
        import traceback
        traceback.print_exc()
        return
    
    # Actualizar registros en Supabase
    print("\n💾 Actualizando registros en Supabase...")
    
    try:
        batch_size = 1000
        offset = 0
        total_updated = 0
        total_records = 0
        
        while True:
            result = supabase.table('sales_lines')\
                .select('id, product_id')\
                .range(offset, offset + batch_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            total_records += len(result.data)
            
            # Actualizar cada registro con su ciclo de vida
            for row in result.data:
                product_id = row.get('product_id')
                if product_id and product_id in product_lifecycle:
                    lifecycle = product_lifecycle[product_id]
                    
                    # Actualizar el registro
                    try:
                        supabase.table('sales_lines')\
                            .update({'product_life_cycle': lifecycle})\
                            .eq('id', row['id'])\
                            .execute()
                        
                        total_updated += 1
                        
                        if total_updated % 100 == 0:
                            print(f"   📊 Actualizados: {total_updated}/{total_records}")
                    
                    except Exception as e:
                        print(f"   ⚠️ Error actualizando registro {row['id']}: {e}")
            
            # Si obtuvimos menos que el tamaño de página, no hay más datos
            if len(result.data) < batch_size:
                break
            
            offset += batch_size
        
        print(f"\n✅ Actualización completada:")
        print(f"   📊 Total registros procesados: {total_records}")
        print(f"   ✅ Registros actualizados: {total_updated}")
        print(f"   ⚠️ Sin actualizar: {total_records - total_updated}")
    
    except Exception as e:
        print(f"❌ Error actualizando Supabase: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
