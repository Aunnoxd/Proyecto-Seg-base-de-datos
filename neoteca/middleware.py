# /home/rubi/neoteca_sistema/neoteca/middleware.py

from django.utils.deprecation import MiddlewareMixin

class NoCacheMiddleware(MiddlewareMixin):
    """
    Middleware para obligar al navegador a no guardar caché de las páginas.
    Esto evita que al dar 'Atrás' después de un Logout se vean datos sensibles.
    """
    def process_response(self, request, response):
        # Si el usuario está logueado (en Django o en tu sesión personalizada)
        if request.user.is_authenticated or request.session.get('usuario_id'):
            # Agregamos cabeceras HTTP estrictas
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response