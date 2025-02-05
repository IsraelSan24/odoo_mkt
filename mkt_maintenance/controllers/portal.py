from odoo import http
from odoo.http import request
import base64
import json

class EquipmentStatusController(http.Controller):

    @http.route(['/equipmentstatus'], type='http', auth="public", website=True)
    def equipment_status_form(self, **kwargs):
        countries = request.env['res.country'].sudo().search([('code','=','PE')])
        states = request.env['res.country.state'].sudo().search([('country_id.code','=','PE')])
        cities = request.env['res.city'].sudo().search([])
        districts = request.env['l10n_pe.res.city.district'].sudo().search([])
        components = request.env['equipment.component'].sudo().search([])

        values = {
            'countries': countries,
            'states': states,
            'cities': cities,
            'districts': districts,
            'components': components,
        }
        return http.request.render('mkt_maintenance.equipmentstatus', values)


    @http.route(['/equipmentstatus/requested'], type='http', auth="public", website=True, csrf=False)
    def equipmentstatus_requested(self, **post):
        equipment_id = post.get('equipment_id')
        if not equipment_id:
            return request.redirect('/equipmentstatus?error=missing_equipment_id')

        country_id = post.get('country_id')
        state_id = post.get('state_id')
        city_id = post.get('city_id')
        district_id = post.get('district_id')


        file_data = request.httprequest.files

        try:
            equipment_status = request.env['equipment.status'].sudo().create({
                'name': post.get('name'),
                'equipment_id': int(equipment_id),
                'country_id': int(country_id) if country_id else None,
                'state_id': int(state_id) if state_id else None,
                'city_id': int(city_id) if city_id else None,
                'district_id': int(district_id) if district_id else None,
                'status': post.get('status'),
                'state': 'draft',
            })

            fotos = {
                'photo_base': file_data.get('photo_base'),
                'photo_left_side': file_data.get('photo_left_side'),
                'photo_right_side': file_data.get('photo_right_side'),
                'photo_open_screen': file_data.get('photo_open_screen'),
                'photo_open_keyboard': file_data.get('photo_open_keyboard'),
                'photo_closed': file_data.get('photo_closed'),
                'photo_charger': file_data.get('photo_charger'),
            }


            for field_name, file in fotos.items():
                if file:
                    file_content = file.read()
                    encoded_file = base64.b64encode(file_content)
                    equipment_status.write({field_name: encoded_file})

        except ValueError as e:
            return request.redirect('/equipmentstatus?error=invalid_data')

        return request.redirect('/equipmentstatus_requested')


    @http.route(['/equipmentstatus/search_equipment'], type='json', auth="public")
    def search_equipment(self, name):
        equipment = request.env['maintenance.equipment'].sudo().search([('name', '=', name)], limit=1)
        if equipment:
            return {
                'equipment_id': equipment.id,
                'location': equipment.location,
                'category_id': equipment.category_id.name if equipment.category_id else '',
                'model': equipment.model,
                'serial_number': equipment.serial_no,
                'employee_id': equipment.employee_id.name if equipment.employee_id else '',
            }
        return {} 