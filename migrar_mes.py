"""
Migración manual de un mes CERRADO desde Odoo a Supabase (tabla sales_lines).

Estrategia (acordada): el dashboard lee los meses cerrados desde Supabase (rápido y
persistente) y deja el mes en curso en Odoo en vivo. Este script se ejecuta a mano
al cierre de cada mes.

Paridad total con el dashboard en vivo: reutiliza OdooManager.get_sales_lines(), que
arma exactamente las mismas 27 columnas y aplica el mismo filtro (IGV, exclusión de
categorías/internacional). Así lo migrado == lo que mostraba Odoo en vivo.

Idempotente: borra el rango del mes en sales_lines y reinserta. Re-ejecutar es seguro.

USO:
    python migrar_mes.py 2026-05               # migra mayo 2026
    python migrar_mes.py 2026-05 --dry-run     # solo muestra totales, NO escribe
    python migrar_mes.py 2026-03 2026-05       # migra marzo, abril y mayo 2026
    python migrar_mes.py 2026-05 --yes         # sin pedir confirmación
"""

import sys
import calendar
from datetime import datetime

# Salida en UTF-8 (la consola de Windows en cp1252 revienta con los emojis del código)
try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

# Usar el almacén de certificados del SO (Windows). Necesario tras proxies
# corporativos con inspección SSL: el CA raíz está en el store del SO, no en certifi.
try:
    import truststore
    truststore.inject_into_ssl()
except ImportError:
    pass

from odoo_manager import OdooManager
from supabase_manager import SupabaseManager

def _rel(valor):
    """Aplana un campo relacional Odoo [id, 'nombre'] -> (id, nombre)."""
    if isinstance(valor, (list, tuple)) and len(valor) >= 2:
        return valor[0], valor[1]
    return None, None


def _mapear_a_sales_lines(r):
    """Convierte un registro de get_sales_lines (formato Odoo) a una fila plana de sales_lines."""
    move_id, _ = _rel(r.get('move_id'))
    partner_id, _ = _rel(r.get('partner_id'))
    product_id, _ = _rel(r.get('product_id'))
    commercial_line_id, commercial_line_name = _rel(r.get('commercial_line_national_id'))
    invoice_user_id, invoice_user_name = _rel(r.get('invoice_user_id'))
    sales_channel_id, sales_channel_name = _rel(r.get('sales_channel_id'))  # team_id
    route_id, route_name = _rel(r.get('route_id'))
    categ_id, categ_name = _rel(r.get('categ_id'))
    production_line_id, production_line_name = _rel(r.get('production_line_id'))
    pharm_forms_id, pharm_forms_name = _rel(r.get('pharmaceutical_forms_id'))
    pharm_class_id, pharm_class_name = _rel(r.get('pharmacological_classification_id'))
    admin_way_id, admin_way_name = _rel(r.get('administration_way_id'))
    order_user_id, order_user_name = _rel(r.get('order_user_id'))
    shipping_id, shipping_name = _rel(r.get('partner_shipping_id'))
    doc_type_id, doc_type_name = _rel(r.get('l10n_latam_document_type_id'))
    state_id, state_name = _rel(r.get('state_id'))

    # El dashboard en vivo (Odoo) usa 'balance' (ya corregido de signo) como monto.
    # Mantenemos price_subtotal == balance para que los totales coincidan exactamente.
    balance = float(r.get('balance') or 0)

    return {
        # Factura / asiento
        'move_id': move_id,
        'move_name': r.get('move_name'),
        'move_state': r.get('move_state'),
        'payment_state': r.get('payment_state'),
        'invoice_date': r.get('invoice_date'),
        'invoice_origin': r.get('invoice_origin'),

        # Cliente
        'partner_id': partner_id,
        'partner_name': r.get('partner_name'),
        'vat': r.get('vat'),

        # Producto
        'product_id': product_id,
        'product_name': r.get('name'),
        'default_code': r.get('default_code'),
        'quantity': float(r.get('quantity') or 0),
        'price_unit': float(r.get('price_unit') or 0),
        'price_subtotal': balance,
        'balance': balance,

        # Línea comercial
        'commercial_line_national_id': commercial_line_id,
        'commercial_line_name': commercial_line_name,

        # Vendedor (factura)
        'invoice_user_id': invoice_user_id,
        'invoice_user_name': invoice_user_name,

        # Canal de venta (team)
        'sales_channel_id': sales_channel_id,
        'sales_channel_name': sales_channel_name,

        # Ruta / zona
        'route_id': route_id,
        'route_name': route_name,

        # Categoría
        'categ_id': categ_id,
        'categ_name': categ_name,

        # Línea de producción
        'production_line_id': production_line_id,
        'production_line_name': production_line_name,

        # Forma farmacéutica
        'pharmaceutical_forms_id': pharm_forms_id,
        'pharmaceutical_forms_name': pharm_forms_name,

        # Clasificación farmacológica
        'pharmacological_classification_id': pharm_class_id,
        'pharmacological_classification_name': pharm_class_name,

        # Vía de administración
        'administration_way_id': admin_way_id,
        'administration_way_name': admin_way_name,

        # Ciclo de vida (IPN)
        'product_life_cycle': r.get('product_life_cycle'),

        # Orden de venta
        'order_name': r.get('order_name'),
        'order_date': r.get('order_date'),
        'order_state': r.get('order_state'),
        'order_user_id': order_user_id,
        'order_user_name': order_user_name,
        'order_origin': r.get('order_origin'),

        # Envío
        'partner_shipping_id': shipping_id,
        'partner_shipping_name': shipping_name,
        'delivery_observations': r.get('delivery_observations'),
        'client_order_ref': r.get('client_order_ref'),

        # Tipo de documento
        'l10n_latam_document_type_id': doc_type_id,
        'document_type_name': doc_type_name,

        # Geografía
        'state_id': state_id,
        'state_name': state_name,
        'city': r.get('city'),
    }


def _rango_mes(anio, mes):
    ultimo_dia = calendar.monthrange(anio, mes)[1]
    return f"{anio}-{mes:02d}-01", f"{anio}-{mes:02d}-{ultimo_dia:02d}"


def migrar_mes(odoo, supabase_mgr, anio, mes, dry_run=False, auto_yes=False):
    """Migra un único mes (anio, mes) de Odoo a la tabla del año."""
    fecha_inicio, fecha_fin = _rango_mes(anio, mes)
    etiqueta = f"{anio}-{mes:02d}"
    # Tabla destino derivada del mismo mapeo que usa la lectura del dashboard,
    # así escritura y lectura nunca se desincronizan.
    tabla = supabase_mgr._get_table_for_year(anio)

    print("\n" + "=" * 80)
    print(f"🔄 MIGRACIÓN {etiqueta}  ({fecha_inicio} → {fecha_fin})")
    print("=" * 80)

    # Validación: no migrar el mes en curso ni meses futuros
    hoy = datetime.now()
    if anio > hoy.year or (anio == hoy.year and mes >= hoy.month):
        print(f"⛔ {etiqueta} es el mes en curso o futuro. Solo se migran meses CERRADOS. Omitido.")
        return False

    # 1) Traer de Odoo con paridad total (mismo método que el dashboard en vivo)
    print("📥 Obteniendo líneas desde Odoo (get_sales_lines, sin límite)...")
    registros = odoo.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=None)
    if not registros:
        print(f"⚠️ Odoo no devolvió registros para {etiqueta}. Nada que migrar.")
        return False

    filas = [_mapear_a_sales_lines(r) for r in registros]
    total_odoo = sum(f['balance'] for f in filas)
    print(f"   ✅ {len(filas)} líneas | Total ventas Odoo: S/ {total_odoo:,.2f}")

    # Conteo actual en Supabase para el mes
    actual = supabase_mgr.supabase.table(tabla)\
        .select('id', count='exact')\
        .gte('invoice_date', fecha_inicio)\
        .lte('invoice_date', fecha_fin)\
        .limit(1).execute()
    print(f"   📊 Actualmente en Supabase ({tabla}) para {etiqueta}: {actual.count} registros")

    if dry_run:
        print("   🧪 --dry-run: NO se escribe nada. Muestra de la primera fila mapeada:")
        muestra = filas[0]
        for k in ('invoice_date', 'partner_name', 'product_name', 'sales_channel_name',
                  'commercial_line_name', 'price_subtotal', 'product_life_cycle'):
            print(f"        {k}: {muestra.get(k)}")
        return True

    if not auto_yes:
        resp = input(f"\n⚠️ Esto BORRA {etiqueta} en {tabla} y reinserta {len(filas)} filas. ¿Continuar? (SI/no): ")
        if resp.strip().upper() != 'SI':
            print("❌ Cancelado.")
            return False

    # 2) Borrar el mes (idempotencia)
    print(f"🗑️  Borrando {etiqueta} en {tabla}...")
    supabase_mgr.supabase.table(tabla)\
        .delete()\
        .gte('invoice_date', fecha_inicio)\
        .lte('invoice_date', fecha_fin)\
        .execute()

    # 3) Insertar en lotes
    print("📤 Insertando...")
    batch = 100
    insertados = 0
    for i in range(0, len(filas), batch):
        lote = filas[i:i + batch]
        supabase_mgr.supabase.table(tabla).insert(lote).execute()
        insertados += len(lote)
        print(f"   ✅ {insertados}/{len(filas)}")

    # 4) Verificación de totales
    total_sb = 0.0
    page, offset = 1000, 0
    while True:
        res = supabase_mgr.supabase.table(tabla)\
            .select('price_subtotal')\
            .gte('invoice_date', fecha_inicio).lte('invoice_date', fecha_fin)\
            .range(offset, offset + page - 1).execute()
        if not res.data:
            break
        total_sb += sum(float(x['price_subtotal'] or 0) for x in res.data)
        if len(res.data) < page:
            break
        offset += page

    diff = abs(total_odoo - total_sb)
    print("-" * 80)
    print(f"   Insertados: {insertados}")
    print(f"   Total Odoo:     S/ {total_odoo:,.2f}")
    print(f"   Total Supabase: S/ {total_sb:,.2f}")
    print(f"   Diferencia:     S/ {diff:,.2f}")
    print("🎉 OK, totales coinciden." if diff < 1 else "⚠️ Revisa la diferencia.")
    return True


def _parse_mes(arg):
    anio, mes = arg.split('-')
    return int(anio), int(mes)


def main():
    args = [a for a in sys.argv[1:]]
    dry_run = '--dry-run' in args
    auto_yes = '--yes' in args
    meses = [a for a in args if not a.startswith('--')]

    if not meses:
        print(__doc__)
        return

    # Rango si vienen dos meses (YYYY-MM YYYY-MM), si no, lista de meses sueltos
    if len(meses) == 2 and meses[0] <= meses[1]:
        a0, m0 = _parse_mes(meses[0])
        a1, m1 = _parse_mes(meses[1])
        objetivo = []
        a, m = a0, m0
        while (a, m) <= (a1, m1):
            objetivo.append((a, m))
            m += 1
            if m > 12:
                m = 1
                a += 1
    else:
        objetivo = [_parse_mes(x) for x in meses]

    odoo = OdooManager()
    if not odoo.uid:
        print("❌ No se pudo conectar a Odoo.")
        return
    supabase_mgr = SupabaseManager()

    for anio, mes in objetivo:
        migrar_mes(odoo, supabase_mgr, anio, mes, dry_run=dry_run, auto_yes=auto_yes)


if __name__ == '__main__':
    main()
