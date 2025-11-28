from odoo import api, fields, models, _
from odoo.exceptions import ValidationError
import math
import json

class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    check_in_latitude = fields.Float(digits="Location", readonly=True)
    check_in_latitude_text = fields.Char("Check-in Latitude", compute="_compute_check_in_latitude_text")
    check_in_longitude = fields.Float(digits="Location", readonly=True)
    check_in_longitude_text = fields.Char("Check-in Longitude", compute="_compute_check_in_longitude_text")
    check_out_latitude = fields.Float(digits="Location", readonly=True)
    check_out_latitude_text = fields.Char("Check-out Latitude", compute="_compute_check_out_latitude_text")
    check_out_longitude = fields.Float(digits="Location", readonly=True)
    check_out_longitude_text = fields.Char("Check-out Longitude", compute="_compute_check_out_longitude_text")
    user_ip = fields.Char(string="User IP")

    # OFFICE_LATITUDE = -12.0919523
    # OFFICE_LONGITUDE = -77.0696065
    # MAX_DISTANCE_KM = 1

    # HP_LATITUDE = -12.0982048
    # HP_LONGITUDE = -77.0291521
    
    # within_allowed_area = fields.Boolean("Within Allowed Area", compute="_compute_within_allowed_area", store=True)

    MAX_DISTANCE_KM = 1
    HP_LATITUDE = 0.0  # Replace with actual latitude
    HP_LONGITUDE = 0.0  # Replace with actual longitude

    within_allowed_area = fields.Boolean("Within Allowed Area", readonly=True)

    # Campo para almacenar datos de ubicación para el mapa
    map_location_data = fields.Text(
        string="Map Location Data", 
        compute='_compute_map_location_data',
        store=False
    )

    def _compute_map_location_data(self):
        """Prepara los datos para el widget del mapa en formato JSON"""
        for record in self:
            data = {
                'check_in_lat': record.check_in_latitude or 0.0,
                'check_in_lng': record.check_in_longitude or 0.0,
                'check_out_lat': record.check_out_latitude or 0.0,
                'check_out_lng': record.check_out_longitude or 0.0,
                'has_check_in': bool(record.check_in_latitude and record.check_in_longitude),
                'has_check_out': bool(record.check_out_latitude and record.check_out_longitude),
            }
            
            # Agregar datos de ubicación de trabajo si existe
            if record.employee_id and record.employee_id.work_geolocation_id:
                work_loc = record.employee_id.work_geolocation_id
                data['work_location'] = {
                    'name': work_loc.name or 'Ubicación de trabajo',
                    'lat': float(work_loc.latitude) if work_loc.latitude else 0.0,
                    'lng': float(work_loc.longitude) if work_loc.longitude else 0.0,
                    'radius': float(work_loc.proximity_radius) if work_loc.proximity_radius else 1.0,
                }
            else:
                data['work_location'] = None
            
            record.map_location_data = json.dumps(data)
            
            # Log para depuración
            if record.check_in_latitude:
                _logger = self.env['ir.logging']
                _logger.sudo().create({
                    'name': 'Map Location Data',
                    'type': 'server',
                    'level': 'INFO',
                    'message': f'Computed map data for attendance {record.id}: {record.map_location_data}',
                    'func': '_compute_map_location_data',
                    'path': 'hr_attendance_geolocation',
                    'line': '0',
                })

    @api.model
    def create(self, vals):
        if "within_allowed_area" not in vals:
            vals["within_allowed_area"] = self._compute_within_allowed_area(vals)
        return super().create(vals)
    

    def write(self, vals):
        for record in self:
            if not record.within_allowed_area and ("check_in_latitude" in vals or "check_in_longitude" in vals):
                combined_vals = {
                    "employee_id": vals.get("employee_id", record.employee_id.id),
                    "check_in_latitude": vals.get("check_in_latitude", record.check_in_latitude),
                    "check_in_longitude": vals.get("check_in_longitude", record.check_in_longitude),
                }
                vals["within_allowed_area"] = self._compute_within_allowed_area(combined_vals)
        return super().write(vals)

    # @api.depends("check_in_latitude", "check_in_longitude")
    # def _compute_within_allowed_area(self):
    #     for record in self:
    #         if record.check_in_latitude and record.check_in_longitude:
    #             distance = self._haversine_distance(
    #                 record.check_in_latitude, record.check_in_longitude,
    #                 self.HP_LATITUDE, self.HP_LONGITUDE
    #             )
    #             record.within_allowed_area = distance <= self.MAX_DISTANCE_KM
    #         else:
    #             record.within_allowed_area = False

    def _compute_within_allowed_area(self, data: dict):
        employee = self.env['hr.employee'].browse(data["employee_id"])
        latitude = data.get("check_in_latitude") 
        longitude = data.get("check_in_longitude")

        if employee.work_geolocation_id and latitude and longitude:
            distance = self._haversine_distance(
                latitude, longitude,
                employee.work_geolocation_id.latitude,
                employee.work_geolocation_id.longitude
            )
            return distance <= employee.work_geolocation_id.proximity_radius
        return False


    @api.model
    def register_geolocated_attendance(self, latitude, longitude, ip, employee_id=None, action_type=None):
        """Registers attendance only if the user is within the allowed radius."""
        if not latitude or not longitude:
            raise ValidationError(_("Could not retrieve your location."))

        # Calculate distance
        distance = self._haversine_distance(latitude, longitude, self.HP_LATITUDE, self.HP_LONGITUDE)
        if distance > self.MAX_DISTANCE_KM:
            raise ValidationError(_("You are outside the allowed area for attendance check-in/out."))

        # Get employee from the passed ID or from current user
        employee = self.env['hr.employee'].browse(employee_id) if employee_id else self.env.user.employee_id
        if not employee:
            raise ValidationError(_("You do not have an assigned employee."))

        # Check if this is a sign-in or sign-out
        if action_type == 'sign_out' or (not action_type and employee.attendance_state == 'checked_in'):
            attendance = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                ('check_out', '=', False)
            ], limit=1)
            if attendance:
                attendance.write({
                    'check_out': fields.Datetime.now(),
                    'check_out_latitude': latitude,
                    'check_out_longitude': longitude,
                    'user_ip': ip,
                })
                return {'success': True}
            else:
                raise ValidationError(_("Cannot check out: No matching check-in found."))
        else:
            attendance = self.create({
                'employee_id': employee.id,
                'check_in': fields.Datetime.now(),
                'check_in_latitude': latitude,
                'check_in_longitude': longitude,
                'user_ip': ip,
            })
            return {'success': True, 'attendance_id': attendance.id}

    def _haversine_distance(self, lat1, lon1, lat2, lon2):
        """Calculates the distance between two geographic points in km."""
        R = 6371  # Earth's radius in km
        dLat = math.radians(lat2 - lat1)
        dLon = math.radians(lon2 - lon1)
        a = math.sin(dLat/2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon/2) ** 2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        return R * c

    def _get_raw_value_from_geolocation(self, dd):
        d = int(dd)
        m = int((dd - d) * 60)
        s = round((dd - d - m / 60) * 3600.00, 2)
        return "%sº %s' %s'" % (abs(d), abs(m), abs(s))

    def _get_latitude_raw_value(self, dd):
        return "%s %s" % ("N" if dd >= 0 else "S", self._get_raw_value_from_geolocation(dd))

    def _get_longitude_raw_value(self, dd):
        return "%s %s" % ("E" if dd >= 0 else "W", self._get_raw_value_from_geolocation(dd))

    @api.depends("check_in_latitude")
    def _compute_check_in_latitude_text(self):
        for item in self:
            item.check_in_latitude_text = self._get_latitude_raw_value(item.check_in_latitude) if item.check_in_latitude else False

    @api.depends("check_in_longitude")
    def _compute_check_in_longitude_text(self):
        for item in self:
            item.check_in_longitude_text = self._get_longitude_raw_value(item.check_in_longitude) if item.check_in_longitude else False

    @api.depends("check_out_latitude")
    def _compute_check_out_latitude_text(self):
        for item in self:
            item.check_out_latitude_text = self._get_latitude_raw_value(item.check_out_latitude) if item.check_out_latitude else False

    @api.depends("check_out_longitude")
    def _compute_check_out_longitude_text(self):
        for item in self:
            item.check_out_longitude_text = self._get_longitude_raw_value(item.check_out_longitude) if item.check_out_longitude else False
