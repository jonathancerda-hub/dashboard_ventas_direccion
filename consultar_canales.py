# Script temporal para consultar todos los canales de venta disponibles en Odoo

from odoo_manager import OdooManager
from datetime import datetime, timedelta

# Crear instancia de OdooManager
odoo = OdooManager()

print("=" * 80)
print("CONSULTANDO CANALES DE VENTA (crm.team / sales_channel_id)")
print("=" * 80)

try:
    # Consultar todos los equipos de ventas (canales)
    teams = odoo.models.execute_kw(
        odoo.db, odoo.uid, odoo.password, 'crm.team', 'search_read',
        [[]],
        {
            'fields': ['id', 'name', 'active'],
            'context': {'lang': 'es_PE'}
        }
    )
    
    print(f"\n✅ Total de equipos/canales encontrados: {len(teams)}\n")
    
    print("ID  | NOMBRE DEL CANAL                                            | Activo")
    print("-" * 85)
    
    for team in sorted(teams, key=lambda x: x['name']):
        team_id = str(team['id']).ljust(3)
        name = team['name'].ljust(55)
        active = "✓" if team.get('active', True) else "✗"
        
        print(f"{team_id} | {name} | {active:^6}")
    
    print("\n" + "=" * 80)
    print("ANÁLISIS DE CLIENTES POR CANAL")
    print("=" * 80)
    
    # Consultar distribución de clientes por canal
    partners_by_channel = odoo.models.execute_kw(
        odoo.db, odoo.uid, odoo.password, 'res.partner', 'read_group',
        [[('sales_channel_id', '!=', False), ('customer_rank', '>', 0)]],
        {'fields': ['sales_channel_id'], 'groupby': ['sales_channel_id'], 'lazy': False}
    )
    
    print(f"\n📊 Distribución de clientes por canal:\n")
    print("CANAL                                      | Cantidad de Clientes")
    print("-" * 70)
    
    total_clientes = 0
    for group in sorted(partners_by_channel, key=lambda x: x.get('__count', 0), reverse=True):
        channel_info = group.get('sales_channel_id')
        channel_name = channel_info[1] if channel_info else 'Sin Canal'
        count = group.get('__count', 0)
        total_clientes += count
        
        print(f"{channel_name.ljust(42)} | {count:>6}")
    
    print("-" * 70)
    print(f"{'TOTAL'.ljust(42)} | {total_clientes:>6}")
    
    print("\n" + "=" * 80)
    print("VENTAS POR CANAL (ÚLTIMOS 3 MESES)")
    print("=" * 80)
    
    # Consultar ventas de los últimos 3 meses por canal
    fecha_fin = datetime.now().strftime('%Y-%m-%d')
    fecha_inicio = (datetime.now() - timedelta(days=90)).strftime('%Y-%m-%d')
    
    # Obtener algunas ventas recientes para ver qué canales están activos
    sales_by_channel = {}
    sales_lines = odoo.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=1000)
    
    for line in sales_lines:
        channel = line.get('sales_channel_id')
        if channel and isinstance(channel, list) and len(channel) > 1:
            channel_name = channel[1]
        else:
            channel_name = 'Sin Canal'
        
        if channel_name not in sales_by_channel:
            sales_by_channel[channel_name] = {'count': 0, 'total': 0}
        
        sales_by_channel[channel_name]['count'] += 1
        sales_by_channel[channel_name]['total'] += line.get('balance', 0)
    
    print(f"\n📈 Ventas activas por canal ({fecha_inicio} a {fecha_fin}):\n")
    print("CANAL                                      | Líneas | Monto Total")
    print("-" * 75)
    
    for channel_name in sorted(sales_by_channel.keys(), key=lambda x: sales_by_channel[x]['total'], reverse=True):
        data = sales_by_channel[channel_name]
        print(f"{channel_name.ljust(42)} | {data['count']:>6} | S/ {data['total']:>12,.2f}")
    
    print("\n" + "=" * 80)
    print("IDENTIFICACIÓN DE CANALES PRINCIPALES")
    print("=" * 80)
    
    # Identificar patrones en los nombres
    digital_keywords = ['DIGITAL', 'ECOMMERCE', 'WEB', 'ONLINE', 'E-COMMERCE']
    nacional_keywords = ['NACIONAL', 'PERU', 'PERÚ', 'LOCAL', 'DOMESTIC']
    
    print("\n🔍 Análisis de nombres de canales:\n")
    
    canales_digitales = []
    canales_nacionales = []
    otros_canales = []
    
    for team in teams:
        name_upper = team['name'].upper()
        if any(keyword in name_upper for keyword in digital_keywords):
            canales_digitales.append(team['name'])
        elif any(keyword in name_upper for keyword in nacional_keywords):
            canales_nacionales.append(team['name'])
        else:
            otros_canales.append(team['name'])
    
    print("📱 CANALES DIGITALES/ECOMMERCE:")
    for canal in canales_digitales:
        print(f"   - {canal}")
    
    print("\n🏪 CANALES NACIONALES/DISTRIBUIDORES:")
    for canal in canales_nacionales:
        print(f"   - {canal}")
    
    print("\n📦 OTROS CANALES:")
    for canal in otros_canales:
        print(f"   - {canal}")
    
except Exception as e:
    print(f"❌ Error consultando canales: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 80)
print("CONSULTA FINALIZADA")
print("=" * 80)
