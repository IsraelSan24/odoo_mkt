# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import Response
import json
from datetime import datetime, timedelta


class HrAttendanceGeolocation(http.Controller):
    """
    Controlador para sincronización de asistencias con aplicación Android
    Maneja registro de entrada/salida con coordenadas GPS
    """

    @http.route('/api/attendance/hours/<user_id>/<day_week>', auth='user', methods=['GET'])
    def get_attendance_hours(self, user_id, day_week, **kw):
        try:
            calendar_id = http.request.env['hr.employee'].sudo() \
                .search([('user_id', '=', int(user_id))]).resource_calendar_id.id
            hours = http.request.env['resource.calendar.attendance'].sudo() \
                .search_read([('calendar_id', '=', int(calendar_id)), ('dayofweek', '=', day_week)],
                             ['hour_from', 'hour_to'])
            return self.build_response(hours)
        except Exception as e:
            return self.build_response({'err': str(e)})

    @http.route('/api/attendance', auth='user', methods=['POST'], csrf=False)
    def insert_attendance(self, **kw):
        try:
            print("=== ATTENDANCE REQUEST START ===")
            
            # Obtener datos JSON
            request_data = http.request.httprequest.get_data()
            print(f"Raw request data: {request_data}")
            
            if not request_data:
                print("ERROR: No request data received")
                return self.build_response({'success': False, 'error': 'No data received'})
            
            try:
                attendance_data = json.loads(request_data.decode('utf-8'))
                print(f"Parsed attendance_data: {attendance_data}")
            except json.JSONDecodeError as e:
                print(f"JSON decode error: {str(e)}")
                return self.build_response({'success': False, 'error': 'Invalid JSON data'})
            
            # Verificar campos requeridos
            if not attendance_data.get('check_in'):
                print("ERROR: Missing check_in field")
                return self.build_response({'success': False, 'error': 'check_in field is required'})
            
            # Obtener usuario actual
            current_user = http.request.env.user
            print(f"Current user: {current_user.id} - {current_user.name}")
            
            # Buscar empleado por user_id
            employee = http.request.env['hr.employee'].sudo().search([
                ('user_id', '=', current_user.id)
            ], limit=1)
            
            if not employee:
                print(f"No employee found for user {current_user.id}")
                # Usar el employee_id que viene en los datos si no encuentra empleado por user_id
                employee_id = attendance_data.get('employee_id')
                if employee_id:
                    employee = http.request.env['hr.employee'].sudo().browse(employee_id)
                    if not employee.exists():
                        print(f"Employee {employee_id} does not exist")
                        return self.build_response({
                            'success': False, 
                            'error': f'Employee {employee_id} not found'
                        })
                else:
                    print("No employee_id provided in request")
                    return self.build_response({
                        'success': False, 
                        'error': 'No employee found for current user'
                    })
            
            employee_id = employee.id
            print(f"Using employee ID: {employee_id}")
            
            # Verificar fecha de check_in
            check_in_str = attendance_data['check_in']
            print(f"Check-in time: {check_in_str}")
            
            try:
                # Validar formato de fecha
                check_in_dt = datetime.strptime(check_in_str, '%Y-%m-%d %H:%M:%S')
                today_str = check_in_dt.strftime('%Y-%m-%d')
                print(f"Check-in date: {today_str}")
            except ValueError as e:
                print(f"Date parsing error: {str(e)}")
                return self.build_response({
                    'success': False, 
                    'error': f'Invalid date format: {check_in_str}'
                })
            
            # Verificar si es entrada o salida
            check_out_str = attendance_data.get('check_out')

            if not check_out_str:  # Es entrada
                print("Processing CHECK-IN")
                
                # Verificar si ya existe entrada para hoy
                existing = http.request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee_id),
                    ('check_in', '>=', today_str + ' 00:00:00'),
                    ('check_in', '<=', today_str + ' 23:59:59'),
                    ('check_out', '=', False)
                ])
                
                if existing:
                    print(f"Found existing check-in: {existing.id}")
                    return self.build_response({
                        'success': False, 
                        'error': 'Ya existe una entrada registrada para hoy'
                    })
                
                # Obtener coordenadas de entrada
                latitude = attendance_data.get('latitude', 0.0)
                longitude = attendance_data.get('longitude', 0.0)
                print(f"Check-in coordinates: lat={latitude}, lng={longitude}")
                
                # Crear nueva entrada con coordenadas - USANDO CAMPOS ESTÁNDAR
                vals = {
                    'employee_id': employee_id,
                    'check_in': check_in_str,
                }
                
                # Intentar guardar coordenadas en diferentes posibles campos estándar
                if latitude != 0.0 or longitude != 0.0:
                    # Probar múltiples nombres de campos posibles
                    possible_fields = [
                        {'latitude': 'latitude', 'longitude': 'longitude'},
                        {'latitude': 'check_in_latitude', 'longitude': 'check_in_longitude'}, 
                        {'latitude': 'x_latitude', 'longitude': 'x_longitude'},
                        {'latitude': 'x_check_in_latitude', 'longitude': 'x_check_in_longitude'},
                        {'latitude': 'gps_latitude', 'longitude': 'gps_longitude'}
                    ]
                    
                    # Verificar qué campos existen en el modelo
                    attendance_model = http.request.env['hr.attendance']
                    field_names = attendance_model._fields.keys()
                    print(f"Available fields in hr.attendance: {list(field_names)}")
                    
                    coords_saved = False
                    for field_set in possible_fields:
                        lat_field = field_set['latitude']
                        lng_field = field_set['longitude']
                        
                        if lat_field in field_names and lng_field in field_names:
                            vals[lat_field] = latitude
                            vals[lng_field] = longitude
                            print(f"Using coordinate fields: {lat_field}, {lng_field}")
                            coords_saved = True
                            break
                    
                    if not coords_saved:
                        print("No suitable coordinate fields found, saving as text fields")
                        # Como fallback, crear campos personalizados dinámicamente
                        vals['x_latitude'] = str(latitude)
                        vals['x_longitude'] = str(longitude)
                
                print(f"Creating attendance with vals: {vals}")
                
                try:
                    new_attendance = http.request.env['hr.attendance'].sudo().create(vals)
                    print(f"Created attendance ID: {new_attendance.id}")
                    
                    return self.build_response({
                        'success': True, 
                        'message': 'Entrada registrada correctamente',
                        'data': {
                            'attendance_id': new_attendance.id,
                            'latitude': latitude,
                            'longitude': longitude
                        }
                    })
                    
                except Exception as create_error: 
                    print(f"Error creating attendance: {str(create_error)}")
                    print(f"Error details: {repr(create_error)}")
                    return self.build_response({
                        'success': False, 
                        'error': f'Error creating attendance: {str(create_error)}'
                    })

            else:  # Es salida (check_out no está vacío)
                print("Processing CHECK-OUT")
                
                # Buscar entrada del día sin salida O con salida existente (para permitir actualización)
                existing = http.request.env['hr.attendance'].sudo().search([
                    ('employee_id', '=', employee_id),
                    ('check_in', '>=', today_str + ' 00:00:00'),
                    ('check_in', '<=', today_str + ' 23:59:59'),
                ], limit=1)
                
                if not existing:
                    print("No check-in found for check-out")
                    return self.build_response({
                        'success': False, 
                        'error': 'No se encontró entrada para registrar salida'
                    })
                
                # Verificar si es primera salida o actualización
                is_update = bool(existing.check_out)
                action_type = "actualizada" if is_update else "registrada"
                
                print(f"Check-out type: {'UPDATE' if is_update else 'NEW'}")
                print(f"Existing check_out: {existing.check_out}")
                
                # Obtener coordenadas de salida
                latitude = attendance_data.get('latitude', 0.0)
                longitude = attendance_data.get('longitude', 0.0)
                print(f"Check-out coordinates: lat={latitude}, lng={longitude}")
                
                # Preparar datos de actualización
                update_vals = {'check_out': check_out_str}
                
                # Intentar guardar coordenadas de salida
                if latitude != 0.0 or longitude != 0.0:
                    attendance_model = http.request.env['hr.attendance']
                    field_names = attendance_model._fields.keys()
                    
                    # Campos posibles para check-out
                    possible_checkout_fields = [
                        {'latitude': 'checkout_latitude', 'longitude': 'checkout_longitude'},
                        {'latitude': 'check_out_latitude', 'longitude': 'check_out_longitude'},
                        {'latitude': 'x_checkout_latitude', 'longitude': 'x_checkout_longitude'},
                        {'latitude': 'x_check_out_latitude', 'longitude': 'x_check_out_longitude'}
                    ]
                    
                    coords_saved = False
                    for field_set in possible_checkout_fields:
                        lat_field = field_set['latitude']
                        lng_field = field_set['longitude']
                        
                        if lat_field in field_names and lng_field in field_names:
                            update_vals[lat_field] = latitude
                            update_vals[lng_field] = longitude
                            print(f"Using checkout coordinate fields: {lat_field}, {lng_field}")
                            coords_saved = True
                            break
                    
                    if not coords_saved:
                        print("No suitable checkout coordinate fields found, using fallback")
                        update_vals['x_checkout_latitude'] = str(latitude)
                        update_vals['x_checkout_longitude'] = str(longitude)
                
                print(f"Updating attendance with vals: {update_vals}")
                
                try:
                    existing.sudo().write(update_vals)
                    print(f"Updated attendance {existing.id} with check-out and coordinates")
                    
                    return self.build_response({
                        'success': True, 
                        'message': f'Salida {action_type} correctamente',
                        'data': {
                            'attendance_id': existing.id,
                            'latitude': latitude,
                            'longitude': longitude,
                            'is_update': is_update,
                            'previous_checkout': str(existing.check_out) if is_update else None
                        }
                    })
                    
                except Exception as update_error:
                    print(f"Error updating attendance: {str(update_error)}")
                    print(f"Error details: {repr(update_error)}")
                    return self.build_response({
                        'success': False, 
                        'error': f'Error updating attendance: {str(update_error)}'
                    })

        except Exception as e:
            print(f"=== GENERAL ERROR ===")
            print(f"Error: {str(e)}")
            import traceback
            traceback.print_exc()
            
            return self.build_response({
                'success': False, 
                'error': f'Server error: {str(e)}'
            })


    @http.route('/api/employee/<user_id>', auth='user', methods=['GET'])
    def get_employee(self, user_id, **kw):
        try:
            print(f"Getting employee for user_id: {user_id}")
            
            # Buscar empleado
            employees = http.request.env['hr.employee'].sudo().search([('user_id', '=', int(user_id))])
            
            if not employees:
                print(f"No employee found for user_id: {user_id}")
                # En lugar de error, devolver datos básicos usando el user_id
                return self.build_response({
                    'id': int(user_id),
                    'name': 'Usuario',
                    'department_id': 1,
                    'work_email': '',
                    'work_phone': '',
                    'active': True
                })
            
            employee = employees[0]
            employee_data = {
                'id': employee.id,
                'name': employee.name or 'Sin nombre',
                'department_id': employee.department_id.id if employee.department_id else 1,
                'work_email': employee.work_email or '',
                'work_phone': employee.work_phone or '',
                'active': employee.active
            }

            print(f"Employee data: {employee_data}")
            return self.build_response(employee_data)
            
        except Exception as e:
            print(f"Error in get_employee: {str(e)}")
            # Fallback: devolver datos usando user_id
            return self.build_response({
                'id': int(user_id),
                'name': 'Usuario',
                'department_id': 1,
                'work_email': '',
                'work_phone': '',
                'active': True
            })

    

    @http.route('/api/attendance/history/<employee_id>', auth='user', methods=['GET'])
    def get_attendance_history(self, employee_id, **kw):
        try:
            print(f"Searching attendance for employee_id: {employee_id}")
            
            # Obtener los últimos 30 días de asistencias
            thirty_days_ago = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
            print(f"Date range from: {thirty_days_ago}")
            
            attendances = http.request.env['hr.attendance'].sudo().search_read([
                ('employee_id', '=', int(employee_id)),
                ('check_in', '>=', thirty_days_ago + ' 00:00:00')
            ], [
                'id', 'check_in', 'check_out', 'worked_hours'
            ], order='check_in desc')
            
            print(f"Found {len(attendances)} attendance records")
            
            # Formatear los datos para el cliente
            formatted_attendances = []
            for attendance in attendances:
                # Asegurar que worked_hours sea un número válido
                worked_hours_value = attendance.get('worked_hours', 0.0)
                if worked_hours_value is False or worked_hours_value is None:
                    worked_hours_value = 0.0
                    
                formatted_attendance = {
                    'id': attendance['id'],
                    'check_in': attendance['check_in'].strftime('%Y-%m-%d %H:%M:%S') if attendance['check_in'] else '',
                    'check_out': attendance['check_out'].strftime('%Y-%m-%d %H:%M:%S') if attendance['check_out'] else '',
                    'worked_hours': f"{worked_hours_value:.1f} hrs",
                    'name': attendance['check_in'].strftime('%Y-%m-%d') if attendance['check_in'] else '',
                    'display_name': f"Asistencia {attendance['check_in'].strftime('%d/%m/%Y') if attendance['check_in'] else 'N/A'}"
                }
                formatted_attendances.append(formatted_attendance)
            
            print(f"Returning formatted attendances: {len(formatted_attendances)} records")
            return self.build_response(formatted_attendances)
            
        except Exception as e:
            print(f"Error in get_attendance_history: {str(e)}")
            import traceback
            traceback.print_exc()
            return self.build_response([])

    @http.route('/api/attendance/today/<employee_id>', auth='user', methods=['GET'])
    def get_today_attendance(self, employee_id, **kw):
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            attendance = http.request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', int(employee_id)),
                ('check_in', '>=', today + ' 00:00:00'),
                ('check_in', '<=', today + ' 23:59:59')
            ], limit=1)
            
            if attendance:
                return self.build_response({
                    'id': attendance.id,
                    'check_in': attendance.check_in,
                    'check_out': attendance.check_out if attendance.check_out else None,
                    'has_check_in': bool(attendance.check_in),
                    'has_check_out': bool(attendance.check_out)
                })
            else:
                return self.build_response({
                    'has_check_in': False,
                    'has_check_out': False
                })
                
        except Exception as e:
            return self.build_response({'error': str(e)})


    # Método helper para debugging
    @http.route('/api/debug/employee/<employee_id>', auth='user', methods=['GET'])
    def debug_employee_attendance(self, employee_id, **kw):
        try:
            # Verificar que el empleado existe
            employee = http.request.env['hr.employee'].sudo().browse(int(employee_id))
            if not employee.exists():
                return self.build_response({'error': f'Employee {employee_id} not found'})
            
            # Obtener asistencias recientes
            attendances = http.request.env['hr.attendance'].sudo().search([
                ('employee_id', '=', int(employee_id))
            ], limit=5, order='check_in desc')
            
            result = {
                'employee_exists': True,
                'employee_name': employee.name,
                'recent_attendances': [{
                    'id': att.id,
                    'check_in': att.check_in,
                    'check_out': att.check_out,
                    'worked_hours': att.worked_hours
                } for att in attendances]
            }
            
            return self.build_response(result)
        except Exception as e:
            return self.build_response({'error': str(e)})

    
    @http.route('/api/test/coordinates', auth='user', methods=['POST'], csrf=False)
    def test_coordinates(self, **kw):
        try:
            request_data = http.request.httprequest.get_data()
            attendance_data = json.loads(request_data.decode('utf-8'))
            
            return self.build_response({
                'success': True,
                'received_data': attendance_data,
                'latitude': attendance_data.get('latitude'),
                'longitude': attendance_data.get('longitude'),
                'check_in': attendance_data.get('check_in'),
                'check_out': attendance_data.get('check_out'),
                'employee_id': attendance_data.get('employee_id'),
                'department_id': attendance_data.get('department_id')
            })
        except Exception as e:
            return self.build_response({
                'success': False,
                'error': str(e)
            })

    @http.route('/api/debug/attendance_fields', auth='user', methods=['GET'])
    def debug_attendance_fields(self, **kw):
        try:
            attendance_model = http.request.env['hr.attendance']
            field_names = list(attendance_model._fields.keys())
            
            # Buscar campos relacionados con coordenadas
            coord_fields = [f for f in field_names if any(keyword in f.lower() for keyword in ['lat', 'lng', 'long', 'coord', 'gps', 'x_', 'location'])]
            
            return self.build_response({
                'success': True,
                'total_fields': len(field_names),
                'all_fields': sorted(field_names),
                'coordinate_related_fields': sorted(coord_fields),
                'suggested_fields': [
                    'latitude', 'longitude',
                    'check_in_latitude', 'check_in_longitude',
                    'check_out_latitude', 'check_out_longitude',
                    'x_latitude', 'x_longitude'
                ]
            })
        except Exception as e:
            return self.build_response({
                'success': False,
                'error': str(e)
            })
   
    def build_response(self, entity):
        response = json.dumps(entity, ensure_ascii=False, default=str).encode('utf8')
        return Response(response, content_type='application/json;charset=utf-8', status=200)