# generate_cache.py
"""
Script para generar el caché de todos los meses del año actual y anterior.
Debe ejecutarse en el mismo entorno que app.py (con variables de entorno y dependencias).
"""
import os
import calendar
from datetime import datetime
from app import get_cached_data, save_to_cache, is_current_month, data_manager, gs_manager

def generar_cache_para_mes(año, mes):
    if is_current_month(año, mes):
        print(f"No se genera caché para el mes actual: {año}-{mes:02d}")
        return
    if get_cached_data(año, mes):
        print(f"Ya existe caché para {año}-{mes:02d}")
        return
    print(f"Generando caché para {año}-{mes:02d} ...")
    # Lógica similar a dashboard, pero solo lo necesario para el caché
    fecha_inicio = f"{año}-{mes:02d}-01"
    ultimo_dia = calendar.monthrange(año, mes)[1]
    fecha_fin = f"{año}-{mes:02d}-{ultimo_dia}"
    try:
        sales_data = data_manager.get_sales_lines(date_from=fecha_inicio, date_to=fecha_fin, limit=5000)
        metas_historicas = gs_manager.read_metas_por_linea()
        metas_del_mes_raw = metas_historicas.get(f"{año}-{mes:02d}", {}).get('metas', {})
        total_venta = sum(float(s.get('balance', 0)) for s in sales_data)
        total_meta = sum(metas_del_mes_raw.values())
        kpis = {
            'meta_total': total_meta,
            'venta_total': total_venta,
            'porcentaje_avance': (total_venta / total_meta * 100) if total_meta > 0 else 0
        }

        # --- Calcular tendencia_12_meses ---
        tendencia_12_meses = []
        from datetime import datetime as dt
        fecha_base = dt(año, mes, 1)
        for i in range(11, -1, -1):
            if mes - i > 0:
                mes_num = mes - i
                año_mes = año
            else:
                mes_num = 12 + (mes - i)
                año_mes = año - 1
            key_mes = f"{año_mes}-{mes_num:02d}"
            # Obtener ventas y metas del mes
            ventas_mes = 0
            for s in sales_data:
                invoice_date = s.get('invoice_date')
                if invoice_date:
                    if isinstance(invoice_date, str):
                        try:
                            fecha_venta = dt.strptime(invoice_date, '%Y-%m-%d')
                        except:
                            continue
                    else:
                        fecha_venta = invoice_date
                    if fecha_venta.year == año_mes and fecha_venta.month == mes_num:
                        balance = s.get('balance', 0)
                        if isinstance(balance, str):
                            balance = float(balance.replace(',', ''))
                        ventas_mes += balance
            metas_mes = metas_historicas.get(key_mes, {}).get('metas', {})
            meta_mes = sum(metas_mes.values())
            fecha_mes = dt(año_mes, mes_num, 1)
            tendencia_12_meses.append({
                'mes': key_mes,
                'mes_nombre': fecha_mes.strftime('%b %Y'),
                'venta': ventas_mes,
                'meta': meta_mes,
                'cumplimiento': (ventas_mes / meta_mes * 100) if meta_mes > 0 else 0
            })

        cache_data = {'kpis': kpis, 'tendencia_12_meses': tendencia_12_meses}
        save_to_cache(año, mes, cache_data)
        print(f"✅ Caché generado para {año}-{mes:02d} (incluye tendencia_12_meses)")
    except Exception as e:
        print(f"❌ Error generando caché para {año}-{mes:02d}: {e}")

def main():
    hoy = datetime.now()
    años = [hoy.year - 1, hoy.year]
    for año in años:
        for mes in range(1, 13):
            generar_cache_para_mes(año, mes)

if __name__ == "__main__":
    main()
