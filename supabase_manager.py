"""
Gestor de datos históricos en Supabase
"""

import os
from dotenv import load_dotenv
from supabase import create_client, Client
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

load_dotenv(override=True)

class SupabaseManager:
    """Gestiona consultas de datos históricos en Supabase"""
    
    def __init__(self):
        supabase_url = os.getenv('SUPABASE_URL', 'https://ppmbwujtfueilifisxhs.supabase.co')
        supabase_key = os.getenv('SUPABASE_KEY')
        
        if not supabase_key:
            raise ValueError("⚠️ SUPABASE_KEY no está configurada en el archivo .env")
        
        self.supabase: Client = create_client(supabase_url, supabase_key)
        self._year_cache = {}  # Cache para años disponibles
        self._month_cache = {}  # Cache para meses ya migrados (año, mes) -> bool
        
        # Caché: Deshabilitar en Render Free (red lenta), habilitar en local
        # Render Free Tier tiene red 0.1 CPU compartida, cargar 31K registros = timeout
        self.enable_cache = os.getenv('ENABLE_SUPABASE_CACHE', 'false').lower() == 'true'
        
        if self.enable_cache:
            # Caché de datos para evitar cargar 31K+ registros múltiples veces
            self._all_data_cache = {}  # {table_name: [all records]}
            self._cache_loaded = {}  # {table_name: bool}
            print("✅ Conexión a Supabase establecida (CACHÉ HABILITADO)")
        else:
            print("✅ Conexión a Supabase establecida (modo bajo consumo RAM)")
    
    def _get_table_for_year(self, año: int) -> str:
        """Determina qué tabla usar según el año"""
        if año == 2025:
            return 'ventas_odoo_2025'
        return 'sales_lines'  # Tabla genérica para otros años
    
    def _get_all_sales_for_year(self, año: int) -> List[Dict]:
        """
        Obtiene TODOS los registros de un año sin filtros de fecha
        Workaround para bug de Supabase que pierde datos con .gte()/.lte() + paginación
        
        Args:
            año: Año a consultar
            
        Returns:
            Lista con todos los registros del año
        """
        table_name = self._get_table_for_year(año)
        print(f"📥 Cargando TODOS los registros de {table_name}...")
        
        all_data = []
        page_size = 1000
        offset = 0
        
        while True:
            result = self.supabase.table(table_name)\
                .select('*')\
                .range(offset, offset + page_size - 1)\
                .execute()
            
            if not result.data:
                break
            
            all_data.extend(result.data)
            
            if len(result.data) < page_size:
                break
            
            offset += page_size
        
        print(f"✅ Cargados {len(all_data)} registros totales")
        return all_data
    
    def get_sales_data(self, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """
        Obtiene líneas de venta de Supabase para un rango de fechas
        
        Dos modos de operación:
        1. CON CACHÉ (enable_cache=True): Carga todo y filtra en Python (preciso pero usa mucha RAM)
        2. SIN CACHÉ (enable_cache=False): Query directo con filtros (bajo consumo RAM, Render Free compatible)
        
        Args:
            fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'
            fecha_fin: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Lista de diccionarios con las líneas de venta filtradas por fecha
        """
        try:
            año = int(fecha_inicio[:4])
            table_name = self._get_table_for_year(año)
            
            if self.enable_cache:
                # MODO CACHÉ: Para desarrollo local con RAM suficiente
                if not self._cache_loaded.get(table_name, False):
                    print(f"📥 Cargando TODOS los registros de {table_name} en caché...")
                    all_data = []
                    page_size = 1000
                    offset = 0
                    
                    while True:
                        result = self.supabase.table(table_name)\
                            .select('*')\
                            .range(offset, offset + page_size - 1)\
                            .execute()
                        
                        if not result.data:
                            break
                        
                        all_data.extend(result.data)
                        
                        if len(result.data) < page_size:
                            break
                        
                        offset += page_size
                    
                    self._all_data_cache[table_name] = all_data
                    self._cache_loaded[table_name] = True
                    print(f"✅ Caché cargado: {len(all_data)} registros")
                else:
                    all_data = self._all_data_cache[table_name]
                    print(f"⚡ Usando caché: {len(all_data)} registros")
                
                # Filtrar por fechas en Python
                filtered_data = [
                    record for record in all_data
                    if record.get('invoice_date') and 
                       fecha_inicio <= record.get('invoice_date') <= fecha_fin
                ]
            else:
                # MODO SIN CACHÉ: Query directo con filtros (para Render Free Tier)
                print(f"🔍 Consultando {table_name} con filtros: {fecha_inicio} a {fecha_fin}")
                filtered_data = []
                page_size = 1000
                offset = 0
                
                while True:
                    result = self.supabase.table(table_name)\
                        .select('*')\
                        .gte('invoice_date', fecha_inicio)\
                        .lte('invoice_date', fecha_fin)\
                        .range(offset, offset + page_size - 1)\
                        .execute()
                    
                    if not result.data:
                        break
                    
                    filtered_data.extend(result.data)
                    
                    if len(result.data) < page_size:
                        break
                    
                    offset += page_size
            
            print(f"📊 Supabase: {len(filtered_data)} registros para {fecha_inicio} a {fecha_fin}")
            return filtered_data
        except Exception as e:
            print(f"⚠️ Error obteniendo datos de Supabase: {e}")
            return []
    
    def get_active_partners_count(self, date_from: str, date_to: str) -> int:
        """
        Cuenta el número de clientes únicos que han comprado en un rango de fechas
        
        Args:
            date_from: Fecha inicial 'YYYY-MM-DD'
            date_to: Fecha final 'YYYY-MM-DD'
        
        Returns:
            Número de clientes únicos
        """
        try:
            año = int(date_from[:4])
            table_name = self._get_table_for_year(año)
            result = self.supabase.table(table_name)\
                .select('partner_id')\
                .gte('invoice_date', date_from)\
                .lte('invoice_date', date_to)\
                .execute()
            
            if result.data:
                # Extraer IDs únicos de clientes
                partner_ids = set()
                for row in result.data:
                    partner_id = row.get('partner_id')
                    if partner_id:
                        partner_ids.add(partner_id)
                
                count = len(partner_ids)
                print(f"✅ Clientes únicos en Supabase ({date_from} a {date_to}): {count}")
                return count
            
            return 0
            
        except Exception as e:
            print(f"❌ Error al contar clientes en Supabase: {e}")
            return 0
    
    def get_ipn_total(self, date_from: str, date_to: str) -> float:
        """
        Suma de ventas (price_subtotal) de productos NUEVOS (IPN) en el rango de fechas.
        IPN = product_life_cycle == 'nuevo' (misma definición que el cálculo mensual).
        """
        try:
            año = int(date_from[:4])
            table_name = self._get_table_for_year(año)
            total = 0.0
            page_size = 1000
            offset = 0
            while True:
                result = self.supabase.table(table_name)\
                    .select('price_subtotal')\
                    .eq('product_life_cycle', 'nuevo')\
                    .gte('invoice_date', date_from)\
                    .lte('invoice_date', date_to)\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                if not result.data:
                    break
                total += sum(float(r.get('price_subtotal') or 0) for r in result.data)
                if len(result.data) < page_size:
                    break
                offset += page_size
            print(f"💊 IPN Supabase ({date_from}..{date_to}): S/ {total:,.2f}")
            return total
        except Exception as e:
            print(f"⚠️ Error get_ipn_total: {e}")
            return 0.0

    def get_active_partners_by_channel(self, date_from: str, date_to: str) -> dict:
        """
        Obtiene el número de clientes únicos por canal de venta
        
        Args:
            date_from: Fecha inicial 'YYYY-MM-DD'
            date_to: Fecha final 'YYYY-MM-DD'
        
        Returns:
            Dict con {nombre_canal: num_clientes}
        """
        try:
            año = int(date_from[:4])
            table_name = self._get_table_for_year(año)
            result = self.supabase.table(table_name)\
                .select('partner_id, sales_channel_name')\
                .gte('invoice_date', date_from)\
                .lte('invoice_date', date_to)\
                .execute()
            
            if not result.data:
                return {}
            
            # Agrupar clientes por canal
            clientes_por_canal = {}
            for row in result.data:
                canal = row.get('sales_channel_name') or 'SIN CANAL'
                partner_id = row.get('partner_id')
                
                if not partner_id:
                    continue
                
                if canal not in clientes_por_canal:
                    clientes_por_canal[canal] = set()
                
                clientes_por_canal[canal].add(partner_id)
            
            # Convertir sets a conteos
            resultado = {canal: len(clientes) for canal, clientes in clientes_por_canal.items()}
            
            print(f"✅ Clientes por canal en Supabase ({date_from} a {date_to}):")
            for canal, count in resultado.items():
                print(f"   - {canal}: {count} clientes")
            
            return resultado
            
        except Exception as e:
            print(f"❌ Error al obtener clientes por canal en Supabase: {e}")
            return {}
    
    def get_monthly_summary(self, año: int, mes: Optional[int] = None) -> List[Dict]:
        """
        Obtiene resumen mensual de ventas
        
        Args:
            año: Año a consultar
            mes: Mes a consultar (opcional, si no se especifica devuelve todo el año)
        
        Returns:
            Lista de resúmenes mensuales
        """
        try:
            query = self.supabase.table('sales_monthly_summary')\
                .select('*')\
                .eq('año', año)
            
            if mes:
                query = query.eq('mes', mes)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"⚠️ Error obteniendo resumen mensual: {e}")
            return []
    
    def get_sales_by_month(self, fecha_inicio: str, fecha_fin: str) -> Dict[str, float]:
        """
        Obtiene resumen de ventas agrupadas por mes
        Los datos en Supabase YA tienen los filtros aplicados cuando se cargaron desde Odoo
        Solo se agrupa y suma TODOS los registros, sin deduplicar
        
        Args:
            fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'
            fecha_fin: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Diccionario con mes como clave ('enero 2025') y total de ventas como valor
        """
        try:
            resumen = {}
            meses_es = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
                7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }

            # Determinar tabla según el año
            año = int(fecha_inicio[:4])
            table_name = self._get_table_for_year(año)

            print(f"🔍 get_sales_by_month: Consultando {fecha_inicio} a {fecha_fin} en tabla {table_name}")

            # MEMORIA: leer SOLO las 3 columnas necesarias y procesar página por página.
            # Antes se hacía select('*') de todo el año (61 cols x miles de filas) -> OOM
            # en Render Free (512MB). Aquí no acumulamos todas las filas en memoria.
            # Se mantiene el workaround del bug de Supabase: paginar sin filtro de fechas
            # y filtrar el rango en Python.
            page_size = 1000
            offset = 0
            total_registros = 0
            while True:
                result = self.supabase.table(table_name)\
                    .select('invoice_date, balance, price_subtotal')\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                if not result.data:
                    break

                for row in result.data:
                    invoice_date = row.get('invoice_date') or ''
                    if len(invoice_date) < 7:
                        continue
                    if not (fecha_inicio <= invoice_date <= fecha_fin):
                        continue
                    # Usar balance si está disponible (igual que el KPI Venta), sino price_subtotal
                    balance = float(row.get('balance') or row.get('price_subtotal') or 0)
                    a = int(invoice_date[:4])
                    m = int(invoice_date[5:7])
                    mes_nombre = f"{meses_es.get(m, m)} {a}"
                    resumen[mes_nombre] = resumen.get(mes_nombre, 0) + balance
                    total_registros += 1

                if len(result.data) < page_size:
                    break
                offset += page_size

            print(f"📊 Resumen mensual Supabase: {total_registros} registros sumados, {len(resumen)} meses")
            return resumen
            
        except Exception as e:
            print(f"⚠️ Error obteniendo ventas por mes: {e}")
            import traceback
            traceback.print_exc()
            return {}
    
    def get_goals(self, año: int, mes: Optional[int] = None) -> List[Dict]:
        """
        Obtiene metas de ventas
        
        Args:
            año: Año a consultar
            mes: Mes a consultar (opcional)
        
        Returns:
            Lista de metas
        """
        try:
            query = self.supabase.table('sales_goals')\
                .select('*')\
                .eq('año', año)
            
            if mes:
                query = query.eq('mes', mes)
            
            result = query.execute()
            return result.data
        except Exception as e:
            print(f"⚠️ Error obteniendo metas: {e}")
            return []
    
    def is_year_in_supabase(self, año: int) -> bool:
        """
        Verifica si hay datos de un año específico en Supabase (con cache)
        
        Args:
            año: Año a verificar
        
        Returns:
            True si hay datos, False en caso contrario
        """
        # Usar cache si ya verificamos este año
        if año in self._year_cache:
            print(f"  📌 Cache hit para año {año}: {self._year_cache[año]}")
            return self._year_cache[año]
        
        try:
            table_name = self._get_table_for_year(año)
            # Filtrar por rango de fechas del año completo
            fecha_inicio = f"{año}-01-01"
            fecha_fin = f"{año}-12-31"
            result = self.supabase.table(table_name)\
                .select('id', count='exact')\
                .gte('invoice_date', fecha_inicio)\
                .lte('invoice_date', fecha_fin)\
                .limit(1)\
                .execute()
            
            has_data = result.count > 0 if hasattr(result, 'count') else len(result.data) > 0
            self._year_cache[año] = has_data
            print(f"  📊 Verificado año {año} en {table_name}: {result.count if hasattr(result, 'count') else len(result.data)} registros, has_data={has_data}")
            return has_data
        except Exception as e:
            print(f"⚠️ Error verificando año en Supabase: {e}")
            return False

    def is_month_in_supabase(self, año: int, mes: int) -> bool:
        """
        Verifica si un mes específico (año, mes) ya fue migrado a Supabase (con cache).

        Se usa para enrutar meses CERRADOS de 2026+ a Supabase en lugar de Odoo en vivo.
        """
        clave = (año, mes)
        if clave in self._month_cache:
            return self._month_cache[clave]

        try:
            import calendar
            table_name = self._get_table_for_year(año)
            ultimo_dia = calendar.monthrange(año, mes)[1]
            fecha_inicio = f"{año}-{mes:02d}-01"
            fecha_fin = f"{año}-{mes:02d}-{ultimo_dia:02d}"
            result = self.supabase.table(table_name)\
                .select('id', count='exact')\
                .gte('invoice_date', fecha_inicio)\
                .lte('invoice_date', fecha_fin)\
                .limit(1)\
                .execute()

            has_data = result.count > 0 if hasattr(result, 'count') else len(result.data) > 0
            self._month_cache[clave] = has_data
            print(f"  📊 Verificado mes {año}-{mes:02d} en {table_name}: has_data={has_data}")
            return has_data
        except Exception as e:
            print(f"⚠️ Error verificando mes en Supabase: {e}")
            return False

    def get_dashboard_data(self, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """
        Obtiene datos formateados para el dashboard, compatible con OdooManager
        Convierte el formato de Supabase al formato de Odoo con arrays [id, "nombre"]
        
        Args:
            fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'
            fecha_fin: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Lista de líneas de venta en el formato esperado por el dashboard
        """
        sales_data = self.get_sales_data(fecha_inicio, fecha_fin)
        
        # Formatear datos para compatibilidad con el dashboard (formato Odoo)
        formatted_data = []
        for sale in sales_data:
            # Convertir campos simples de Supabase a formato Odoo [id, "nombre"]
            # NO aplicar abs() - las notas de crédito deben ser negativas
            price_subtotal = float(sale.get('price_subtotal', 0))
            balance = float(sale.get('balance', 0))
            
            # Mapeo de campos de la nueva estructura de Supabase
            formatted_sale = {
                # Factura/Move
                'invoice_id': sale.get('move_id'),
                'move_id': [sale.get('move_id'), sale.get('move_name')] if sale.get('move_id') else False,
                'invoice_name': sale.get('move_name'),
                'move_name': sale.get('move_name'),
                'invoice_date': sale.get('invoice_date'),
                'move_state': sale.get('move_state'),
                'payment_state': sale.get('payment_state'),
                
                # Cliente
                'partner_id': [sale.get('partner_id'), sale.get('partner_name')] if sale.get('partner_id') else False,
                'partner_name': sale.get('partner_name'),
                'vat': sale.get('vat'),
                
                # Producto
                'product_id': [sale.get('product_id'), sale.get('product_name')] if sale.get('product_id') else False,
                'product_name': sale.get('product_name'),
                'name': sale.get('product_name'),  # Odoo usa 'name' para nombre de producto
                'product_code': sale.get('default_code'),
                'default_code': sale.get('default_code'),
                'quantity': float(sale.get('quantity', 0)),
                'price_unit': float(sale.get('price_unit', 0)),
                'price_subtotal': price_subtotal,
                'balance': balance,
                
                # Línea Comercial (usando el ID y nombre reales)
                'commercial_line_national_id': [sale.get('commercial_line_national_id'), sale.get('commercial_line_name')] if sale.get('commercial_line_national_id') else False,
                'linea_comercial': sale.get('commercial_line_name'),
                
                # Vendedor (invoice_user)
                'invoice_user_id': [sale.get('invoice_user_id'), sale.get('invoice_user_name')] if sale.get('invoice_user_id') else False,
                'vendedor': sale.get('invoice_user_name'),
                
                # Canal de venta
                'sales_channel_id': [sale.get('sales_channel_id'), sale.get('sales_channel_name')] if sale.get('sales_channel_id') else False,
                'canal': sale.get('sales_channel_name'),
                
                # Ruta/Zona
                'route_id': [sale.get('route_id'), sale.get('route_name')] if sale.get('route_id') else False,
                'zona': sale.get('route_name'),
                'ruta': sale.get('route_name'),
                
                # Categoría de producto
                'categ_id': [sale.get('categ_id'), sale.get('categ_name')] if sale.get('categ_id') else False,
                'categoria_producto': sale.get('categ_name'),
                
                # Línea de producción
                'production_line_id': [sale.get('production_line_id'), sale.get('production_line_name')] if sale.get('production_line_id') else False,
                'production_line': sale.get('production_line_name'),
                
                # Forma farmacéutica
                'pharmaceutical_forms_id': [sale.get('pharmaceutical_forms_id'), sale.get('pharmaceutical_forms_name')] if sale.get('pharmaceutical_forms_id') else False,
                'pharmaceutical_form': sale.get('pharmaceutical_forms_name'),
                
                # Clasificación farmacológica
                'pharmacological_classification_id': [sale.get('pharmacological_classification_id'), sale.get('pharmacological_classification_name')] if sale.get('pharmacological_classification_id') else False,
                'pharmacological_classification': sale.get('pharmacological_classification_name'),
                
                # Vía de administración
                'administration_way_id': [sale.get('administration_way_id'), sale.get('administration_way_name')] if sale.get('administration_way_id') else False,
                'administration_way': sale.get('administration_way_name'),
                
                # Ciclo de vida del producto (crítico para IPN)
                'product_life_cycle': sale.get('product_life_cycle'),
                
                # Orden de venta
                'order_id': sale.get('order_id'),
                'order_name': sale.get('order_name'),
                'order_date': sale.get('order_date'),
                'order_state': sale.get('order_state'),
                'order_user_id': [sale.get('order_user_id'), sale.get('order_user_name')] if sale.get('order_user_id') else False,
                'order_user_name': sale.get('order_user_name'),
                'invoice_origin': sale.get('invoice_origin'),
                'order_origin': sale.get('order_origin'),
                
                # Dirección de envío
                'partner_shipping_id': [sale.get('partner_shipping_id'), sale.get('partner_shipping_name')] if sale.get('partner_shipping_id') else False,
                'partner_shipping_name': sale.get('partner_shipping_name'),
                
                # Observaciones y referencias
                'delivery_observations': sale.get('delivery_observations'),
                'client_order_ref': sale.get('client_order_ref'),
                
                # Tipo de documento
                'l10n_latam_document_type_id': [sale.get('l10n_latam_document_type_id'), sale.get('document_type_name')] if sale.get('l10n_latam_document_type_id') else False,
                'document_type_name': sale.get('document_type_name'),
                
                # Estado/Provincia (agregados desde Odoo)
                'state_id': [sale.get('state_id'), sale.get('state_name')] if sale.get('state_id') else False,
                'ciudad': sale.get('city'),
                'city': sale.get('city'),
                'provincia': sale.get('state_name'),
            }
            formatted_data.append(formatted_sale)
        
        return formatted_data
    
    def get_unique_clients_count(self, fecha_inicio: str, fecha_fin: str) -> int:
        """
        Cuenta clientes únicos en un rango de fechas
        
        Args:
            fecha_inicio: Fecha inicial
            fecha_fin: Fecha final
        
        Returns:
            Número de clientes únicos
        """
        try:
            # Usar select con distinct para contar clientes únicos directamente
            # Sin límite para obtener todos los registros
            all_partners = set()
            page_size = 1000
            offset = 0
            año = int(fecha_inicio[:4])
            table_name = self._get_table_for_year(año)
            
            while True:
                result = self.supabase.table(table_name)\
                    .select('partner_id')\
                    .gte('invoice_date', fecha_inicio)\
                    .lte('invoice_date', fecha_fin)\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                
                if not result.data:
                    break
                
                for sale in result.data:
                    if sale.get('partner_id'):
                        all_partners.add(sale['partner_id'])
                
                if len(result.data) < page_size:
                    break
                
                offset += page_size
            
            return len(all_partners)
            
        except Exception as e:
            print(f"⚠️ Error contando clientes únicos: {e}")
            return 0
    
    def read_metas_from_supabase(self, año: int = None) -> Dict:
        """
        Lee las metas desde Supabase tabla metas_ventas_2026
        
        Args:
            año: Año para filtrar las metas (opcional). Si no se proporciona, devuelve todas las metas.
        
        Returns:
            Dict con formato: {
                '2026-01': {
                    'metas': {'agrovet': 1300000.0, 'petmedica': 1300000.0, ...},
                    'metas_ipn': {'agrovet': 760000.0, 'petmedica': 400000.0, ...},
                    'total': 3014000.0,
                    'total_ipn': 1839089.0
                },
                ...
            }
        """
        try:
            # Consultar todas las metas desde Supabase
            query = self.supabase.table('metas_ventas_2026').select('*')
            
            # Si se especifica un año, filtrar por ese año
            if año:
                query = query.gte('mes', f'{año}-01').lte('mes', f'{año}-12')
            
            result = query.execute()
            
            if not result.data:
                print(f"⚠️ No se encontraron metas en Supabase para año {año}")
                return {}
            
            # Estructurar datos en el formato esperado
            metas_por_linea = {}
            
            for record in result.data:
                mes_key = record.get('mes')  # '2026-01'
                linea = record.get('linea_comercial', '').lower()  # 'AGROVET' -> 'agrovet'
                meta_total = float(record.get('meta_total', 0) or 0)
                meta_ipn = float(record.get('meta_ipn', 0) or 0)
                
                if not mes_key or not linea:
                    continue
                
                # Inicializar el mes si no existe
                if mes_key not in metas_por_linea:
                    metas_por_linea[mes_key] = {
                        'metas': {},
                        'metas_ipn': {},
                        'total': 0.0,
                        'total_ipn': 0.0
                    }
                
                # Agregar meta total
                metas_por_linea[mes_key]['metas'][linea] = meta_total
                
                # Agregar meta IPN
                if meta_ipn > 0:
                    metas_por_linea[mes_key]['metas_ipn'][linea] = meta_ipn
            
            # Calcular totales
            for mes_key in metas_por_linea:
                metas_por_linea[mes_key]['total'] = sum(metas_por_linea[mes_key]['metas'].values())
                metas_por_linea[mes_key]['total_ipn'] = sum(metas_por_linea[mes_key]['metas_ipn'].values())
            
            print(f"✅ Metas cargadas desde Supabase: {len(metas_por_linea)} meses")
            return metas_por_linea
            
        except Exception as e:
            print(f"⚠️ Error al leer metas desde Supabase: {e}")
            return {}
