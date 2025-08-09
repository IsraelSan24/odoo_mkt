# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd.
#    Copyright (C) 2020-TODAY Cybrosys Technologies(<http://www.cybrosys.com>).
#    Author: cybrosys(<https://www.cybrosys.com>)
#
#    This program is free software: you can modify
#    it under the terms of the GNU Affero General Public License (AGPL) as
#    published by the Free Software Foundation, either version 3 of the
#    License, or (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Affero General Public License for more details.
#
#    You should have received a copy of the GNU Affero General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
###################################################################################
import pytz
import sys
import datetime
import logging
import binascii
from datetime import datetime, time
from collections import defaultdict

from . import zklib
from .zkconst import *
from struct import unpack
from odoo import api, fields, models
from odoo import _
from odoo.exceptions import UserError, ValidationError
_logger = logging.getLogger(__name__)
try:
    from zk import ZK, const
except ImportError:
    _logger.error("Please Install pyzk library.")

_logger = logging.getLogger(__name__)


class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(
        string='Biometric Device ID',
        related='employee_id.device_id',
        store=True,
    )


class ZkMachine(models.Model):
    _name = 'zk.machine'
    
    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port No', required=True)
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one('res.company', string='Company', default=lambda self: self.env.user.company_id.id)

    def device_connect(self, zk):
        try:
            conn = zk.connect()
            return conn
        except:
            return False
    
    def clear_attendance(self):
        for info in self:
            try:
                machine_ip = info.name
                zk_port = info.port_no
                timeout = 30
                try:
                    zk = ZK(machine_ip, port=zk_port, timeout=timeout, password=0, force_udp=False, ommit_ping=False)
                except NameError:
                    raise UserError(_("Please install it with 'pip3 install pyzk'."))
                conn = self.device_connect(zk)
                if conn:
                    conn.enable_device()
                    clear_data = zk.get_attendance()
                    if clear_data:
                        # conn.clear_attendance()
                        self._cr.execute("""delete from zk_machine_attendance""")
                        conn.disconnect()
                        raise UserError(_('Attendance Records Deleted.'))
                    else:
                        raise UserError(_('Unable to clear Attendance log. Are you sure attendance log is not empty.'))
                else:
                    raise UserError(
                        _('Unable to connect to Attendance Device. Please use Test Connection button to verify.'))
            except:
                raise ValidationError(
                    'Unable to clear Attendance log. Are you sure attendance device is connected & record is not empty.')

    def getSizeUser(self, zk):
        """Checks a returned packet to see if it returned CMD_PREPARE_DATA,
        indicating that data packets are to be sent

        Returns the amount of bytes that are going to be sent"""
        command = unpack('HHHH', zk.data_recv[:8])[0]
        if command == CMD_PREPARE_DATA:
            size = unpack('I', zk.data_recv[8:12])[0]
            print("size", size)
            return size
        else:
            return False

    def zkgetuser(self, zk):
        """Start a connection with the time clock"""
        try:
            users = zk.get_users()
            print(users)
            return users
        except:
            return False

    @api.model
    def cron_download(self):
        machines = self.env['zk.machine'].search([])
        for machine in machines :
            machine.download_attendance()

    def download_attendance(self):
        _logger.info("++++++++++++ Cron Executed ++++++++++++++++")
        zk_attendance = self.env['zk.machine.attendance']
        att_obj       = self.env['hr.attendance']

        tz_local = pytz.timezone(self.env.user.partner_id.tz or 'GMT')

        for info in self:
            # 1) Conectar al dispositivo
            try:
                zk = ZK(info.name, port=info.port_no, timeout=15,
                    password=0, force_udp=False, ommit_ping=False)
            except NameError:
                raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))
            conn = self.device_connect(zk)
            if not conn:
                raise UserError(_('Unable to connect, please check parameters and network.'))

            # 2) Leer marcaciones
            try:
                raw_att = conn.get_attendance() or []
            except:
                raw_att = []
            if not raw_att:
                raise UserError(_('Unable to get the attendance log, please try again.'))

            # 3) Agrupar por empleado y fecha local
            grouped = defaultdict(list)
            for rec in raw_att:
                grouped[(rec.user_id, rec.timestamp.date())].append(rec.timestamp)

            # 4) Helper: local_to_utc_naive
            def to_utc_naive(dt_local):
                aware = tz_local.localize(dt_local, is_dst=None)
                utc_dt = aware.astimezone(pytz.utc)
                return utc_dt.replace(tzinfo=None)

            # 5) Procesar cada grupo diario
            for (device_id, day), timestamps in grouped.items():
                timestamps.sort()
                dt_in  = timestamps[0]
                dt_out = timestamps[-1]
                if dt_in == dt_out:
                    dt_out = datetime.combine(day, time(23, 59))

                in_naive  = to_utc_naive(dt_in)
                out_naive = to_utc_naive(dt_out)

                in_str  = fields.Datetime.to_string(in_naive)
                out_str = fields.Datetime.to_string(out_naive)

                # 6) Buscar empleado en Odoo
                emp = self.env['hr.employee'].search([('device_id','=',device_id)], limit=1)
                if not emp:
                    _logger.warning("Empleado %s no existe; omitiendo.", device_id)
                    continue

                # 7) Calcular inicio/fin del día en UTC naive
                #    - 00:00 local -> UTC-naive
                #    - 23:59:59 local -> UTC-naive
                local_start = datetime.combine(day, time(0,0))
                local_end   = datetime.combine(day, time(23,59,59))
                start_utc   = to_utc_naive(local_start)
                end_utc     = to_utc_naive(local_end)

                # 8) Crear o actualizar hr.attendance
                existing = att_obj.search([
                    ('employee_id','=', emp.id),
                    ('check_in','>=', start_utc),
                    ('check_in','<=', end_utc),
                ], limit=1)

                vals = {
                    'employee_id': emp.id,
                    'check_in':    in_str,
                    'check_out':   out_str if out_naive > in_naive else False,
                }
                if existing:
                    existing.write(vals)
                else:
                    att_obj.create(vals)

            conn.disconnect()

        return True
