"""
Calcular la suma total de las metas de 2025
"""
import sys
sys.path.insert(0, 'c:\\Users\\jcerda\\Desktop\\DashBoard Direccion\\dashboard-ventas')

from app import load_metas

print("="*80)
print("CALCULANDO SUMA TOTAL DE METAS 2025")
print("="*80)

metas_2025 = load_metas(2025)

suma_total = 0
suma_total_ipn = 0

print("\nDetalle por mes:")
print("-"*80)
for mes_key in sorted(metas_2025.keys()):
    total_mes = metas_2025[mes_key]['total']
    total_ipn_mes = metas_2025[mes_key]['total_ipn']
    suma_total += total_mes
    suma_total_ipn += total_ipn_mes
    print(f"{mes_key}: S/ {total_mes:,.2f}  (IPN: S/ {total_ipn_mes:,.2f})")

print("="*80)
print(f"✅ SUMA TOTAL META 2025: S/ {suma_total:,.2f}")
print(f"✅ SUMA TOTAL IPN 2025:  S/ {suma_total_ipn:,.2f}")
print("="*80)
