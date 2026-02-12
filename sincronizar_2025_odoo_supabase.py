"""
Script para sincronizar datos de 2025 desde Odoo a Supabase
Obtiene todos los registros de 2025 de Odoo y los inserta en Supabase
"""

from odoo_manager import OdooManager
from supabase_manager import SupabaseManager
from datetime import datetime

def main():
    print("=" * 80)
    print("🔄 SINCRONIZACIÓN ODOO → SUPABASE (Año 2025)")
    print("=" * 80)
    
    # Inicializar managers
    odoo = OdooManager()
    supabase_mgr = SupabaseManager()
    
    if not odoo.uid:
        print("❌ No se pudo conectar a Odoo")
        return
    
    # Paso 1: Obtener total actual en Supabase
    print("\n📊 PASO 1: Verificando datos actuales en Supabase...")
    result_current = supabase_mgr.supabase.table('sales_lines')\
        .select('id', count='exact')\
        .gte('invoice_date', '2025-01-01')\
        .lte('invoice_date', '2025-12-31')\
        .limit(1)\
        .execute()
    
    current_count = result_current.count
    print(f"   ✅ Registros actuales en Supabase: {current_count}")
    
    # Paso 2: Obtener datos de Odoo 2025
    print("\n📊 PASO 2: Obteniendo datos de 2025 desde Odoo...")
    print("   Esto puede tomar varios minutos...")
    
    # Construir dominio igual que en get_sales_lines
    domain = [
        ('move_id.move_type', 'in', ['out_invoice', 'out_refund']),
        ('move_id.state', '=', 'posted'),
        ('product_id.default_code', '!=', False),
        ('product_id.commercial_line_national_id', '!=', False),
        ('move_id.sales_channel_id.name', '!=', 'INTERNACIONAL'),
        ('product_id.categ_id', 'not in', [315, 333, 304, 314, 318, 339]),
        ('product_id.commercial_line_national_id.name', 'not ilike', 'VENTA INTERNACIONAL'),
        ('move_id.invoice_date', '>=', '2025-01-01'),
        ('move_id.invoice_date', '<=', '2025-12-31')
    ]
    
    # Obtener IDs de todos los registros que cumplen los filtros
    print("   📦 Obteniendo IDs de registros...")
    ids_odoo = odoo.models.execute_kw(
        odoo.db, odoo.uid, odoo.password,
        'account.move.line', 'search',
        [domain],
        {'limit': 0}  # Sin límite, obtener todos
    )
    
    total_odoo = len(ids_odoo)
    print(f"   ✅ Total de registros en Odoo que cumplen filtros: {total_odoo}")
    
    if total_odoo == 0:
        print("\n❌ No se encontraron registros en Odoo para 2025")
        return
    
    # Paso 3: Obtener datos completos en lotes
    print(f"\n📊 PASO 3: Obteniendo datos completos de Odoo...")
    batch_size = 500
    all_lines = []
    
    for i in range(0, total_odoo, batch_size):
        batch_ids = ids_odoo[i:i+batch_size]
        print(f"   Lote {i//batch_size + 1}/{(total_odoo + batch_size - 1)//batch_size}: {len(batch_ids)} registros...")
        
        lines = odoo.models.execute_kw(
            odoo.db, odoo.uid, odoo.password,
            'account.move.line', 'read',
            [batch_ids],
            {
                'fields': [
                    'id', 'move_id', 'partner_id', 'product_id', 'balance',
                    'move_name', 'quantity', 'price_unit', 'display_name'
                ]
            }
        )
        all_lines.extend(lines)
    
    print(f"   ✅ Datos completos obtenidos: {len(all_lines)} líneas")
    
    # Paso 4: Obtener información adicional (facturas, productos, clientes)
    print(f"\n📊 PASO 4: Obteniendo información relacionada...")
    
    move_ids = list(set([line['move_id'][0] for line in all_lines if line.get('move_id')]))
    product_ids = list(set([line['product_id'][0] for line in all_lines if line.get('product_id')]))
    partner_ids = list(set([line['partner_id'][0] for line in all_lines if line.get('partner_id')]))
    
    print(f"   📦 {len(move_ids)} facturas, {len(product_ids)} productos, {len(partner_ids)} clientes")
    
    # Obtener facturas
    print("   📅 Obteniendo facturas...")
    move_data = {}
    for i in range(0, len(move_ids), batch_size):
        batch = move_ids[i:i+batch_size]
        moves = odoo.models.execute_kw(
            odoo.db, odoo.uid, odoo.password,
            'account.move', 'read',
            [batch],
            {'fields': ['id', 'invoice_date', 'name', 'state', 'invoice_origin', 'sales_channel_id']}
        )
        for m in moves:
            move_data[m['id']] = m
    
    # Obtener productos
    print("   📦 Obteniendo productos...")
    product_data = {}
    for i in range(0, len(product_ids), batch_size):
        batch = product_ids[i:i+batch_size]
        products = odoo.models.execute_kw(
            odoo.db, odoo.uid, odoo.password,
            'product.product', 'read',
            [batch],
            {'fields': ['id', 'name', 'default_code', 'commercial_line_national_id']}
        )
        for p in products:
            product_data[p['id']] = p
    
    # Obtener clientes
    print("   👥 Obteniendo clientes...")
    partner_data = {}
    for i in range(0, len(partner_ids), batch_size):
        batch = partner_ids[i:i+batch_size]
        partners = odoo.models.execute_kw(
            odoo.db, odoo.uid, odoo.password,
            'res.partner', 'read',
            [batch],
            {'fields': ['id', 'name', 'vat']}
        )
        for p in partners:
            partner_data[p['id']] = p
    
    print("   ✅ Información relacionada obtenida")
    
    # Paso 5: Preparar datos para inserción
    print(f"\n📊 PASO 5: Preparando datos para inserción...")
    records_to_insert = []
    skipped = 0
    
    for line in all_lines:
        try:
            move_id = line.get('move_id')[0] if line.get('move_id') else None
            product_id = line.get('product_id')[0] if line.get('product_id') else None
            partner_id = line.get('partner_id')[0] if line.get('partner_id') else None
            
            if not all([move_id, product_id, partner_id]):
                skipped += 1
                continue
            
            move = move_data.get(move_id, {})
            product = product_data.get(product_id, {})
            partner = partner_data.get(partner_id, {})
            
            invoice_date = move.get('invoice_date')
            if not invoice_date:
                skipped += 1
                continue
            
            commercial_line = product.get('commercial_line_national_id')
            commercial_line_name = commercial_line[1] if commercial_line and isinstance(commercial_line, list) else ''
            
            # Balance debe ser != 0
            balance = line.get('balance', 0)
            if balance == 0:
                skipped += 1
                continue
            
            record = {
                'odoo_id': line['id'],
                'invoice_date': invoice_date,
                'invoice_name': move.get('name', ''),
                'partner_id': partner_id,
                'partner_name': partner.get('name', ''),
                'product_id': product_id,
                'product_name': product.get('name', ''),
                'product_code': product.get('default_code', ''),
                'commercial_line_name': commercial_line_name,
                'quantity': float(line.get('quantity', 0)),
                'price_unit': float(line.get('price_unit', 0)),
                'price_subtotal': abs(float(balance))  # Usar valor absoluto del balance
            }
            
            records_to_insert.append(record)
            
        except Exception as e:
            print(f"   ⚠️ Error procesando línea {line.get('id')}: {e}")
            skipped += 1
    
    print(f"   ✅ Registros preparados: {len(records_to_insert)}")
    print(f"   ⚠️ Registros omitidos: {skipped}")
    
    # Calcular total
    total_ventas = sum(r['price_subtotal'] for r in records_to_insert)
    print(f"   💰 Total de ventas: S/ {total_ventas:,.2f}")
    
    # Paso 6: Confirmar antes de insertar
    print(f"\n{'='*80}")
    print("📋 RESUMEN:")
    print(f"   • Registros actuales en Supabase: {current_count}")
    print(f"   • Registros en Odoo: {total_odoo}")
    print(f"   • Registros a insertar: {len(records_to_insert)}")
    print(f"   • Total ventas: S/ {total_ventas:,.2f}")
    print(f"{'='*80}")
    
    respuesta = input("\n⚠️ ¿Deseas ELIMINAR los datos actuales e insertar los nuevos? (SI/no): ")
    
    if respuesta.upper() != 'SI':
        print("\n❌ Operación cancelada")
        return
    
    # Paso 7: Eliminar datos actuales
    print(f"\n🗑️ PASO 6: Eliminando datos actuales de 2025 en Supabase...")
    try:
        delete_result = supabase_mgr.supabase.table('sales_lines')\
            .delete()\
            .gte('invoice_date', '2025-01-01')\
            .lte('invoice_date', '2025-12-31')\
            .execute()
        print(f"   ✅ Datos antiguos eliminados")
    except Exception as e:
        print(f"   ⚠️ Error al eliminar: {e}")
        print(f"   Continuando con inserción...")
    
    # Paso 8: Insertar nuevos datos en lotes
    print(f"\n📥 PASO 7: Insertando datos en Supabase...")
    insert_batch_size = 100
    inserted = 0
    errors = 0
    
    for i in range(0, len(records_to_insert), insert_batch_size):
        batch = records_to_insert[i:i+insert_batch_size]
        try:
            supabase_mgr.supabase.table('sales_lines').insert(batch).execute()
            inserted += len(batch)
            print(f"   ✅ Lote {i//insert_batch_size + 1}: {len(batch)} registros insertados ({inserted}/{len(records_to_insert)})")
        except Exception as e:
            print(f"   ❌ Error en lote {i//insert_batch_size + 1}: {e}")
            errors += len(batch)
    
    # Paso 9: Verificar resultado final
    print(f"\n📊 PASO 8: Verificando resultado final...")
    result_final = supabase_mgr.supabase.table('sales_lines')\
        .select('price_subtotal', count='exact')\
        .gte('invoice_date', '2025-01-01')\
        .lte('invoice_date', '2025-12-31')\
        .execute()
    
    final_count = result_final.count
    
    # Calcular total en Supabase
    page_size = 1000
    offset = 0
    total_supabase = 0
    
    while True:
        result = supabase_mgr.supabase.table('sales_lines')\
            .select('price_subtotal')\
            .gte('invoice_date', '2025-01-01')\
            .lte('invoice_date', '2025-12-31')\
            .range(offset, offset + page_size - 1)\
            .execute()
        
        if not result.data:
            break
        
        total_supabase += sum(float(r['price_subtotal']) for r in result.data)
        
        if len(result.data) < page_size:
            break
        
        offset += page_size
    
    print(f"\n{'='*80}")
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print(f"{'='*80}")
    print(f"   • Registros insertados: {inserted}")
    print(f"   • Errores: {errors}")
    print(f"   • Total registros en Supabase: {final_count}")
    print(f"   • Total ventas en Supabase: S/ {total_supabase:,.2f}")
    print(f"   • Diferencia vs Odoo: S/ {abs(total_ventas - total_supabase):,.2f}")
    print(f"{'='*80}")
    
    if abs(total_ventas - total_supabase) < 100:  # Diferencia menor a S/ 100
        print("\n🎉 ¡Sincronización exitosa! Los totales coinciden.")
    else:
        print(f"\n⚠️ Advertencia: Hay diferencia de S/ {abs(total_ventas - total_supabase):,.2f}")

if __name__ == '__main__':
    main()
