from django import template

register = template.Library()

@register.filter
def convertir_tiempo(value):
    """
    Convierte minutos enteros a formato 'Xh Ym' o 'X min'.
    Uso en HTML: {{ libro.tiempo_estimado|convertir_tiempo }}
    """
    try:
        minutos_totales = int(value)
    except (ValueError, TypeError):
        return "0 min"

    if minutos_totales == 0:
        return "0 min"
    
    if minutos_totales < 60:
        return f"{minutos_totales} min"
    
    horas = minutos_totales // 60
    minutos = minutos_totales % 60
    
    if minutos == 0:
        return f"{horas} hrs"
    
    return f"{horas}h {minutos}m"