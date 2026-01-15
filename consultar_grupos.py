"""
Script para consultar los grupos de venta (agr.groups)
"""
import sys
sys.path.append('.')
from odoo_manager import OdooManager

odoo = OdooManager()

print("🔍 Consultando modelo agr.groups...\n")

# Obtener todos los grupos
groups = odoo.models.execute_kw(
    odoo.db, odoo.uid, odoo.password,
    'agr.groups', 'search_read',
    [[]],
    {'fields': ['id', 'name'], 'order': 'name'}
)

print(f"📋 Total de grupos encontrados: {len(groups)}\n")
for group in groups:
    print(f"  ID {group['id']}: {group['name']}")

# Ahora consultar algunos clientes con sus grupos
print("\n\n🧪 Consultando clientes con grupos...")
partners = odoo.models.execute_kw(
    odoo.db, odoo.uid, odoo.password,
    'res.partner', 'search_read',
    [[['customer_rank', '>', 0], ['groups_ids', '!=', False]]],
    {'fields': ['name', 'groups_ids'], 'limit': 10}
)

print(f"\n📊 Ejemplo de {len(partners)} clientes con grupos:")
for partner in partners:
    print(f"\n  {partner['name']}")
    print(f"    Groups IDs: {partner.get('groups_ids', [])}")
