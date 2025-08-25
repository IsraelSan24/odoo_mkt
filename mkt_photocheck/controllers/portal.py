from odoo import _, http
from odoo.http import request
import base64
import json

class Photocheck(http.Controller):

    @http.route('/photocheck', type='http', auth='public', website=True)
    def photocheck(self, **kw):
        """Renderiza el formulario de photocheck con datos filtrados"""
        # Obtener todos los trabajos
        jobs = request.env['photocheck.job'].sudo().search([])
        
        # Obtener todas las ciudades
        citys = request.env['photocheck.city'].sudo().search([])
        
        # Obtener todos los grupos de marcas
        brands = request.env['photocheck.brand.group'].sudo().search([])
        
        # Obtener todos los supervisores con sus ciudades y grupos de marcas
        supervisors = request.env['photocheck.supervisor'].sudo().search([])
        
        values = {
            'jobs': jobs,
            'citys': citys,
            'brands': brands,
            'supervisors': supervisors
        }
        return request.render('mkt_photocheck.request_photocheck', values)

    @http.route('/photocheck/requested', type='http', auth='public', website=True, methods=['POST'], csrf=True)
    def photocheck_requested(self, **post):
        """Procesa el formulario enviado con validaciones mejoradas"""
        
        # Obtener datos del formulario
        dni = post.get('dni')
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        job_id = post.get('job_id')
        city_id = post.get('city_id')
        photocheck_supervisor_id = post.get('photocheck_supervisor_id')
        photocheck_brand_group_id = post.get('photocheck_brand_group_id')
        
        # VALIDACIÓN ACTUALIZADA: Verificar que el supervisor tiene acceso a la marca seleccionada
        if photocheck_supervisor_id and photocheck_brand_group_id:
            supervisor = request.env['photocheck.supervisor'].sudo().browse(int(photocheck_supervisor_id))
            if int(photocheck_brand_group_id) not in supervisor.brand_group_ids.ids:
                # Redirigir con error si la validación falla
                return request.render('website.404', {
                    'error_message': 'El supervisor seleccionado no tiene acceso al grupo de marcas elegido.'
                })
        
        # VALIDACIÓN ACTUALIZADA: Verificar que el supervisor puede trabajar en la ciudad seleccionada
        if photocheck_supervisor_id and city_id:
            supervisor = request.env['photocheck.supervisor'].sudo().browse(int(photocheck_supervisor_id))
            if int(city_id) not in supervisor.city_ids.ids:
                # Redirigir con error si la validación falla
                return request.render('website.404', {
                    'error_message': 'El supervisor seleccionado no puede trabajar en la ciudad elegida.'
                })
        
        # Procesar imagen como en el método original
        if 'photo' in post:
            photo_content = post['photo'].read()
            photo_data64 = base64.b64encode(photo_content)
            post['photo'] = photo_data64
            post['photo_raw'] = photo_data64
        
        # Crear el registro
        new_photo = request.env['photocheck'].sudo().create(post)
        new_photo.sudo().modify_image()
        
        return request.render('mkt_photocheck.photocheck_requested', {})

    @http.route(['/photocheck/get_cities_by_brand'], type='json', auth='public')
    def get_cities_by_brand(self, brand_id):
        """API endpoint para obtener ciudades filtradas por marca"""
        if not brand_id:
            return []
        
        # Buscar supervisores que tengan acceso a esta marca
        supervisors = request.env['photocheck.supervisor'].sudo().search([
            ('brand_group_ids', 'in', [int(brand_id)])
        ])
        
        # Obtener todas las ciudades donde trabajan estos supervisores
        city_ids = set()
        for supervisor in supervisors:
            city_ids.update(supervisor.city_ids.ids)
        
        # Obtener los datos de las ciudades
        cities = request.env['photocheck.city'].sudo().browse(list(city_ids))
        
        return [{
            'id': city.id,
            'name': city.name
        } for city in cities]

    @http.route(['/photocheck/get_supervisors_by_brand_and_city'], type='json', auth='public')
    def get_supervisors_by_brand_and_city(self, brand_id, city_id):
        """API endpoint para obtener supervisores filtrados por marca y ciudad"""
        if not brand_id or not city_id:
            return []
        
        # Buscar supervisores que tengan acceso a la marca Y la ciudad
        supervisors = request.env['photocheck.supervisor'].sudo().search([
            ('brand_group_ids', 'in', [int(brand_id)]),
            ('city_ids', 'in', [int(city_id)])
        ])
        
        return [{
            'id': supervisor.id,
            'name': supervisor.name,
            'brand_group_ids': supervisor.brand_group_ids.ids,
            'city_ids': supervisor.city_ids.ids
        } for supervisor in supervisors]

    # MÉTODOS ANTIGUOS MANTENIDOS PARA COMPATIBILIDAD (OPCIONAL)
    @http.route(['/photocheck/get_supervisors_by_city'], type='json', auth='public')
    def get_supervisors_by_city(self, city_id):
        """API endpoint para obtener supervisores filtrados por ciudad (MÉTODO LEGACY)"""
        if not city_id:
            return []
        
        supervisors = request.env['photocheck.supervisor'].sudo().search([
            ('city_ids', 'in', [int(city_id)])
        ])
        
        return [{
            'id': supervisor.id,
            'name': supervisor.name,
            'brand_group_ids': supervisor.brand_group_ids.ids
        } for supervisor in supervisors]

    @http.route(['/photocheck/get_brands_by_supervisor'], type='json', auth='public')
    def get_brands_by_supervisor(self, supervisor_id):
        """API endpoint para obtener grupos de marcas filtrados por supervisor (MÉTODO LEGACY)"""
        if not supervisor_id:
            return []
        
        supervisor = request.env['photocheck.supervisor'].sudo().browse(int(supervisor_id))
        
        return [{
            'id': brand.id,
            'name': brand.name
        } for brand in supervisor.brand_group_ids]