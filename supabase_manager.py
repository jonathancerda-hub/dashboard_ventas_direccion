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
        print("✅ Conexión a Supabase establecida")
    
    def _get_table_for_year(self, año: int) -> str:
        """Determina qué tabla usar según el año"""
        if año == 2025:
            return 'ventas_odoo_2025'
        return 'sales_lines'  # Tabla genérica para otros años
    
    def get_sales_data(self, fecha_inicio: str, fecha_fin: str) -> List[Dict]:
        """
        Obtiene líneas de venta de Supabase para un rango de fechas
        Incluye paginación para obtener todos los registros
        
        Args:
            fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'
            fecha_fin: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Lista de diccionarios con las líneas de venta
        """
        try:
            # Determinar tabla según el año
            año = int(fecha_inicio[:4])
            table_name = self._get_table_for_year(año)
            
            all_data = []
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
                
                all_data.extend(result.data)
                
                # Si obtuvimos menos que el tamaño de página, no hay más datos
                if len(result.data) < page_size:
                    break
                
                offset += page_size
            
            print(f"📊 Supabase: {len(all_data)} registros obtenidos para {fecha_inicio} a {fecha_fin}")
            return all_data
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
        Obtiene resumen de ventas agrupadas por mes con paginación
        Los datos en Supabase YA tienen los filtros aplicados cuando se cargaron
        Solo se agrupa y suma, sin aplicar filtros adicionales
        
        Args:
            fecha_inicio: Fecha inicial en formato 'YYYY-MM-DD'
            fecha_fin: Fecha final en formato 'YYYY-MM-DD'
        
        Returns:
            Diccionario con mes como clave ('enero 2025') y total de ventas como valor
        """
        try:
            # Agrupar por mes con paginación
            resumen = {}
            meses_es = {
                1: 'enero', 2: 'febrero', 3: 'marzo', 4: 'abril', 5: 'mayo', 6: 'junio',
                7: 'julio', 8: 'agosto', 9: 'septiembre', 10: 'octubre', 11: 'noviembre', 12: 'diciembre'
            }
            
            page_size = 1000
            offset = 0
            total_registros = 0
            
            # Determinar tabla según el año
            año = int(fecha_inicio[:4])
            table_name = self._get_table_for_year(año)
            
            print(f"🔍 get_sales_by_month: Consultando {fecha_inicio} a {fecha_fin} en tabla {table_name}")
            
            while True:
                # Obtener solo invoice_date y price_subtotal, ordenado por fecha
                result = self.supabase.table(table_name)\
                    .select('invoice_date, price_subtotal')\
                    .gte('invoice_date', fecha_inicio)\
                    .lte('invoice_date', fecha_fin)\
                    .order('invoice_date')\
                    .range(offset, offset + page_size - 1)\
                    .execute()
                
                if not result.data:
                    break
                
                for row in result.data:
                    invoice_date = row.get('invoice_date', '')
                    price_subtotal = float(row.get('price_subtotal', 0))
                    
                    if not invoice_date or len(invoice_date) < 7:
                        continue
                    
                    # Extraer año y mes de invoice_date
                    año = int(invoice_date[:4])
                    mes = int(invoice_date[5:7])
                    
                    mes_nombre = f"{meses_es.get(mes, mes)} {año}"
                    resumen[mes_nombre] = resumen.get(mes_nombre, 0) + price_subtotal
                    total_registros += 1
                
                if len(result.data) < page_size:
                    break
                
                offset += page_size
            
            print(f"📊 Resumen mensual Supabase: {total_registros} registros sumados")
            print(f"   {len(resumen)} meses con datos")
            print(f"   Total general: S/ {sum(resumen.values()):,.2f}")
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
            # Aplicar abs() para asegurar que todos los valores sean positivos
            price_subtotal = abs(float(sale.get('price_subtotal', 0)))
            balance = abs(float(sale.get('balance', 0)))
            
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
                
                # NOTA: Los campos provincia/state_id NO existen en la nueva estructura
                # Se necesitará obtener estos datos de otras fuentes o del partner_id
                'state_id': False,
                'ciudad': None,
                'city': None,
                'provincia': None,
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
