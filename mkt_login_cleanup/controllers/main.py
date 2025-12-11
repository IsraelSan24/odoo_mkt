# -*- coding: utf-8 -*-
from odoo import http
from odoo.addons.web.controllers.main import Home
from odoo.addons.auth_signup.controllers.main import AuthSignupHome


class CustomHomeLogin(Home):
    
    @http.route('/web/login', type='http', auth="none")
    def web_login(self, redirect=None, **kw):
        # Limpiar el login (email) - eliminar espacios y convertir a minusculas
        if 'login' in kw and kw['login']:
            kw['login'] = kw['login'].strip().lower()
        
        # Limpiar la contraseña - solo eliminar espacios
        if 'password' in kw and kw['password']:
            kw['password'] = kw['password'].strip()
        
        return super(CustomHomeLogin, self).web_login(redirect, **kw)

class CustomAuthSignup(AuthSignupHome):
    
    @http.route('/web/reset_password', type='http', auth='public', website=True, sitemap=False)
    def web_auth_reset_password(self, *args, **kw):
        # Limpiar el email
        if 'login' in kw and kw['login']:
            kw['login'] = kw['login'].strip().lower()
        
        return super(CustomAuthSignup, self).web_auth_reset_password(*args, **kw)