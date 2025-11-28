# -*- coding: utf-8 -*-
###################################################################################
#
#    Cybrosys Technologies Pvt. Ltd. (adaptado y robustecido)
#    Copyright (C) 2020-TODAY Cybrosys
#
#    Licencia AGPL-3.0
#
###################################################################################
import logging
from collections import defaultdict
from datetime import datetime, time

import pytz

from odoo import api, fields, models, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)

try:
    from zk import ZK, const  # pyzk
except ImportError:
    _logger.error("Please install pyzk: pip3 install pyzk")


# ======================================================================
# Extensión de hr.attendance (opcional, guarda el device_id para auditoría)
# ======================================================================
class HrAttendance(models.Model):
    _inherit = 'hr.attendance'

    device_id = fields.Char(
        string='Biometric Device ID',
        related='employee_id.device_id',
        store=True,
    )


# ======================================================================
# Dispositivo ZK
# ======================================================================
class ZkMachine(models.Model):
    _name = 'zk.machine'
    _description = 'ZKTeco Device'

    # Configuración básica
    name = fields.Char(string='Machine IP', required=True)
    port_no = fields.Integer(string='Port', required=True)
    password = fields.Integer(string='Device Password', default=0)
    use_force_udp = fields.Boolean(string='Force UDP', default=False)
    omit_ping = fields.Boolean(string='Omit Ping', default=False)
    timeout_seconds = fields.Integer(string='Timeout (s)', default=60)

    # Metadatos útiles de operación
    address_id = fields.Many2one('res.partner', string='Working Address')
    company_id = fields.Many2one(
        'res.company', string='Company',
        default=lambda self: self.env.user.company_id.id
    )
    last_sync = fields.Datetime(string='Last Sync')
    last_sync_status = fields.Selection([
        ('ok', 'OK'),
        ('empty', 'Empty'),
        ('error', 'Error')
    ], string='Last Sync Status')
    last_error = fields.Text(string='Last Error')

    # -------------------------
    # Helpers de conexión
    # -------------------------
    def _build_zk(self):
        """Construye el cliente ZK con los parámetros del registro."""
        self.ensure_one()
        try:
            zk = ZK(
                self.name,
                port=self.port_no,
                timeout=self.timeout_seconds or 60,
                password=self.password or 0,
                force_udp=bool(self.use_force_udp),
                ommit_ping=bool(self.omit_ping),
            )
            return zk
        except NameError:
            # pyzk no instalado
            raise UserError(_("Pyzk module not Found. Please install it with 'pip3 install pyzk'."))

    @staticmethod
    def _safe_disconnect(conn):
        try:
            if conn:
                conn.disconnect()
        except Exception:
            pass

    @staticmethod
    def _safe_enable(conn):
        try:
            if conn:
                conn.enable_device()
        except Exception:
            pass

    def device_connect(self, zk):
        """Abre la conexión al dispositivo, retorna conn o False."""
        try:
            return zk.connect()
        except Exception as e:
            _logger.exception("ZK connect failed (%s:%s): %s", self.name, self.port_no, e)
            return False

    # -------------------------
    # Cron: descarga de marcaciones
    # -------------------------
    @api.model
    def cron_download(self):
        """Cron que recorre todos los dispositivos y descarga marcaciones."""
        machines = self.search([])
        for machine in machines:
            try:
                machine.download_attendance()
            except Exception as e:
                _logger.exception("Cron download failed for %s: %s", machine.name, e)
                machine.write({
                    'last_sync': fields.Datetime.now(),
                    'last_sync_status': 'error',
                    'last_error': str(e),
                })

    # -------------------------
    # Limpieza de attendances en el dispositivo (manual)
    # -------------------------
    def clear_attendance(self):
        """Limpia registros de asistencia en el dispositivo. Uso manual."""
        for rec in self:
            conn = None
            try:
                zk = rec._build_zk()
                conn = rec.device_connect(zk)
                if not conn:
                    raise UserError(_('Unable to connect to the device. Use "Test Connection" first.'))

                # Es importante deshabilitar el dispositivo para operaciones críticas
                conn.disable_device()
                try:
                    sizes = {}
                    try:
                        sizes = conn.read_sizes() or {}
                        _logger.info("ZK(%s) sizes before clear: %s", rec.name, sizes)
                    except Exception as e:
                        _logger.warning("Could not read sizes before clear on %s: %s", rec.name, e)

                    # Limpiar en el equipo
                    conn.clear_attendance()

                    # Comprobar nuevamente
                    try:
                        sizes_after = conn.read_sizes() or {}
                        _logger.info("ZK(%s) sizes after clear: %s", rec.name, sizes_after)
                    except Exception:
                        sizes_after = {}

                finally:
                    ZkMachine._safe_enable(conn)

                rec.write({
                    'last_sync': fields.Datetime.now(),
                    'last_sync_status': 'ok',
                    'last_error': False,
                })
                raise UserError(_('Attendance records were cleared from the device.'))

            except UserError:
                raise
            except Exception as e:
                _logger.exception("Unable to clear attendance (%s): %s", rec.name, e)
                raise ValidationError(_('Unable to clear attendance log: %s') % e)
            finally:
                ZkMachine._safe_disconnect(conn)

    # -------------------------
    # Descarga de marcaciones (mejorado)
    # -------------------------
    def download_attendance(self):
        """Descarga marcaciones y crea/actualiza hr.attendance por día/empleado."""
        _logger.info("++++++++++++ ZK Cron Executed ++++++++++++++++")
        Attendance = self.env['hr.attendance']

        # TZ del usuario que ejecuta (fallback GMT)
        tz_local = pytz.timezone(self.env.user.partner_id.tz or 'GMT')

        # --- NUEVO: helper para normalizar el user_id del dispositivo ---
        def _normalize_device_user_id(uid):
            """
            Convierte a str, quita espacios y ceros a la izquierda.
            Si todo eran ceros, retorna '0'.
            """
            s = str(uid).strip()
            if not s:
                return s
            s2 = s.lstrip('0')
            return s2 or '0'

        for info in self:
            conn = None
            last_status = 'error'
            last_error = False
            try:
                # 1) Conectar al dispositivo
                zk = info._build_zk()
                conn = info.device_connect(zk)
                if not conn:
                    raise UserError(_('Unable to connect, please check parameters and network.'))

                # 2) Secuencia recomendada: disable -> read_sizes -> get_attendance -> enable
                conn.disable_device()
                sizes = {}
                try:
                    sizes = conn.read_sizes() or {}
                    _logger.info("ZK(%s) sizes: %s", info.name, sizes)
                except Exception as e:
                    _logger.warning("Could not read sizes on %s: %s", info.name, e)

                # 3) Leer marcaciones (manejo de excepciones con log detallado)
                raw_att = []
                try:
                    raw_att = conn.get_attendance() or []
                except Exception as e:
                    _logger.exception("Error on get_attendance() from %s: %s", info.name, e)
                    raw_att = []

                # 4) Re-habilitar dispositivo siempre
                ZkMachine._safe_enable(conn)

                # Si no hay registros, no romper cron: loggear y salir
                if not raw_att:
                    _logger.warning(
                        "Device %s returned no attendance logs. "
                        "Check if device has local history or is in push-only mode.",
                        info.name
                    )
                    last_status = 'empty'
                    info.write({
                        'last_sync': fields.Datetime.now(),
                        'last_sync_status': last_status,
                        'last_error': False,
                    })
                    continue

                # 5) Agrupar por empleado (user_id del reloj NORMALIZADO) y fecha local
                grouped = defaultdict(list)
                for rec in raw_att:
                    user_key = _normalize_device_user_id(rec.user_id)
                    # rec.timestamp suele venir como naive en hora del dispositivo
                    grouped[(user_key, rec.timestamp.date())].append(rec.timestamp)

                # Helper: convierte datetime local (naive) -> UTC naive (sin tzinfo)
                def to_utc_naive(dt_local):
                    aware = tz_local.localize(dt_local, is_dst=None)
                    utc_dt = aware.astimezone(pytz.utc)
                    return utc_dt.replace(tzinfo=None)

                # 6) Procesar cada grupo diario
                Employee = self.env['hr.employee']
                for (device_user_key, day), timestamps in grouped.items():
                    timestamps.sort()
                    dt_in = timestamps[0]
                    dt_out = timestamps[-1]
                    if dt_in == dt_out:
                        # Si solo hay una marca, usamos 23:59 como salida
                        dt_out = datetime.combine(day, time(23, 59))

                    # Conversión a UTC naive (sin tzinfo) para guardar en BD
                    in_naive = to_utc_naive(dt_in)
                    out_naive = to_utc_naive(dt_out)
                    if out_naive and out_naive <= in_naive:
                        # Seguridad extra: nunca dejar salida <= entrada
                        out_naive = False

                    # 7) Empleado por device_id (SIN ceros a la izquierda)
                    # Busca por clave normalizada y, por seguridad, por el valor original en str.
                    # (En la práctica, debería bastar el normalizado.)
                    candidate_ids = list({device_user_key})  # set->list para únicos
                    emp = Employee.search([('device_id', 'in', candidate_ids)], limit=1)
                    if not emp:
                        _logger.warning("Employee with device_id=%s not found; skipping.", device_user_key)
                        continue

                    # 8) Ventana del día en UTC para localizar solapes
                    local_start = datetime.combine(day, time(0, 0, 0))
                    local_end   = datetime.combine(day, time(23, 59, 59))
                    start_utc   = to_utc_naive(local_start)
                    end_utc     = to_utc_naive(local_end)

                    # Buscar cualquier asistencia SOLAPADA:
                    # (check_in < end_utc) AND (check_out IS NULL OR check_out > start_utc)
                    overlapped = Attendance.search([
                        ('employee_id', '=', emp.id),
                        ('check_in', '<', end_utc),
                        '|', ('check_out', '=', False),
                            ('check_out', '>', start_utc),
                    ])

                    if overlapped:
                        # Fusionar todas las asistencias solapadas con la nueva ventana
                        all_ins = [r.check_in for r in overlapped] + [in_naive]
                        all_outs = [x for x in ([r.check_out for r in overlapped] + [out_naive]) if x]
                        new_in = min(all_ins)
                        new_out = max(all_outs) if all_outs else False

                        # Mantener un registro (el más antiguo por check_in) y borrar el resto
                        keep = overlapped.sorted(key=lambda r: (r.check_in or fields.Datetime.now()))[0]
                        to_remove = (overlapped - keep)
                        vals_merge = {
                            'check_in': fields.Datetime.to_string(new_in),
                            'check_out': fields.Datetime.to_string(new_out) if new_out else False,
                        }
                        keep.write(vals_merge)
                        if to_remove:
                            to_remove.unlink()
                        _logger.debug(
                            "Merged %d overlapped attendances into #%s for emp %s on %s",
                            len(overlapped), keep.id, emp.id, day
                        )
                    else:
                        # No hay solapes: crear normal
                        vals = {
                            'employee_id': emp.id,
                            'check_in': fields.Datetime.to_string(in_naive),
                            'check_out': fields.Datetime.to_string(out_naive) if out_naive else False,
                        }
                        created = Attendance.create(vals)
                        _logger.debug("Created attendance %s for emp %s on %s", created.id, emp.id, day)

                last_status = 'ok'
                info.write({
                    'last_sync': fields.Datetime.now(),
                    'last_sync_status': last_status,
                    'last_error': False,
                })
                _logger.info("Download attendance finished for %s with status OK", info.name)

            except UserError as ue:
                last_error = str(ue)
                _logger.warning("UserError on %s: %s", info.name, last_error)
                info.write({
                    'last_sync': fields.Datetime.now(),
                    'last_sync_status': 'error',
                    'last_error': last_error,
                })
                raise
            except Exception as e:
                last_error = str(e)
                _logger.exception("Unexpected error on %s: %s", info.name, last_error)
                info.write({
                    'last_sync': fields.Datetime.now(),
                    'last_sync_status': 'error',
                    'last_error': last_error,
                })
            finally:
                ZkMachine._safe_disconnect(conn)

        return True
