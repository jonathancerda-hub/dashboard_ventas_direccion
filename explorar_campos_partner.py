"""
Script para explorar campos de res.partner relacionados con grupos de venta
"""
import sys
sys.path.append('.')
from odoo_manager import OdooManager

odoo = OdooManager()

# Obtener campos de res.partner
print("🔍 Buscando campos de res.partner relacionados con 'group' o 'category'...\n")

fields = odoo.models.execute_kw(
    odoo.db, odoo.uid, odoo.password,
    'res.partner', 'fields_get',
    [],
    {'attributes': ['string', 'type', 'relation']}
)

# Filtrar campos relacionados con grupos
campos_relevantes = {}
for field_name, field_info in fields.items():
    field_lower = field_name.lower()
    string_lower = field_info.get('string', '').lower()
    
    if any(keyword in field_lower or keyword in string_lower for keyword in ['group', 'category', 'segment', 'type', 'class']):
        campos_relevantes[field_name] = field_info

print("📋 Campos encontrados:")
for field_name, field_info in campos_relevantes.items():
    print(f"\n  - {field_name}")
    print(f"    Nombre: {field_info.get('string', 'N/A')}")
    print(f"    Tipo: {field_info.get('type', 'N/A')}")
    if field_info.get('relation'):
        print(f"    Relación: {field_info.get('relation')}")

# Obtener un cliente ejemplo para ver sus valores
print("\n\n🧪 Probando con un cliente ejemplo...")
partners = odoo.models.execute_kw(
    odoo.db, odoo.uid, odoo.password,
    'res.partner', 'search_read',
    [[['customer_rank', '>', 0]]],
    {'fields': list(campos_relevantes.keys()), 'limit': 5}
)

print(f"\n📊 Ejemplo de {len(partners)} clientes:")
for i, partner in enumerate(partners, 1):
    print(f"\n{i}. {partner.get('name', 'Sin nombre')}")
    for field in campos_relevantes.keys():
        if field in partner and partner[field]:
            print(f"   {field}: {partner[field]}")
