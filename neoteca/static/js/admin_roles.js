/* static/js/admin_roles.js */

document.addEventListener('DOMContentLoaded', function() {
    const $ = django.jQuery; // Usamos el jQuery de Django

    function toggleInlines() {
        const rol = $('#id_rol').val(); // Obtener valor del rol seleccionado

        // 1. Ocultar todos los inlines primero
        $('#profesor-group').hide();
        $('#estudiante-group').hide();
        $('#tutor-group').hide();

        // 2. Mostrar solo el que corresponde
        if (rol === 'PROFESOR') {
            $('#profesor-group').show();
        } else if (rol === 'ESTUDIANTE') {
            $('#estudiante-group').show();
        } else if (rol === 'TUTOR') {
            $('#tutor-group').show();
        }
        // Si es ADMIN, no mostramos ninguno (o podrías mostrar todos si quisieras)
    }

    // Ejecutar al cargar la página (para usuarios existentes)
    toggleInlines();

    // Ejecutar cada vez que se cambie el select de Rol
    $('#id_rol').change(function() {
        toggleInlines();
    });
});