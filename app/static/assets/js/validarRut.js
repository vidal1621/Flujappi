// Permitir sólo números en el imput
function isNumber(evt) {
    var charCode = evt.which ? evt.which : event.keyCode;
    if (charCode > 31 && (charCode < 48 || charCode > 57) && charCode === 75) return false;

    return true;
}

function checkRut(rut, variable, variable2) {
    if (variable == 1) {
        // Capturando el DIV alerta y mensaje
        /*var alerta = document.getElementById("alerta");*/
        var mensaje = document.getElementById("mensaje"+variable);
    }else {
        // Capturando el DIV alerta y mensaje
        var mensaje = document.getElementById("mensaje"+variable2);
    }
    // Obtiene el valor ingresado quitando puntos y guión.
    var valor = clean(rut.value);

    // Divide el valor ingresado en dígito verificador y resto del RUT.
    cuerpo = valor.slice(0, -1);
    dv = valor.slice(-1).toUpperCase();
    // Separa con un Guión el cuerpo del dígito verificador.
    rut.value = format(rut.value);

    if (cuerpo.length == '0' && rut.length >= 1) {
        mensaje.innerHTML = '<li>El RUT ingresado es correcto.</li>';
        mensaje.style.color = "#28a745";
        if (variable == 1) {
            $("#estadorut_"+variable).val(1);
        }else{
            $("#estadorut_"+variable2).val(1);
        }
        return true;
    }else {
        // Si no cumple con el mínimo ej. (n.nnn.nnn)
        if (cuerpo.length < 7) {

            //rut.setCustomValidity("RUT Incompleto");
            mensaje.innerHTML = '<li>Ingresó un RUT muy corto, el RUT debe ser mayor a 7 Dígitos. Ej: x.xxx.xxx-x</li>';
            mensaje.style.color = "#ffc107";
            if (variable == 1) {
                $("#estadorut_" + variable).val(0);

            } else {
                $("#estadorut_" + variable2).val(0);
            }
            return false;
        }
    }

    // Calcular Dígito Verificador "Método del Módulo 11"
    suma = 0;
    multiplo = 2;

    // Para cada dígito del Cuerpo
    for (i = 1; i <= cuerpo.length; i++) {
        // Obtener su Producto con el Múltiplo Correspondiente
        index = multiplo * valor.charAt(cuerpo.length - i);

        // Sumar al Contador General
        suma = suma + index;

        // Consolidar Múltiplo dentro del rango [2,7]
        if (multiplo < 7) {
            multiplo = multiplo + 1;
        } else {
            multiplo = 2;
        }
    }

    // Calcular Dígito Verificador en base al Módulo 11
    dvEsperado = 11 - (suma % 11);

    // Casos Especiales (0 y K)
    dv = dv == "K" ? 10 : dv;
    dv = dv == 0 ? 11 : dv;

    // Validar que el Cuerpo coincide con su Dígito Verificador
    if (dvEsperado != dv) {
        //rut.setCustomValidity("RUT Inválido");
        mensaje.innerHTML = '<li>El RUT ingresado es no es valido.</li>';
        mensaje.style.color = "#dc3545";
        if (variable == 1) {
            $("#estadorut_"+variable).val(0);
        }else{
            $("#estadorut_"+variable2).val(0);
        }
        return false;
    } else {
        //rut.setCustomValidity("RUT Válido");
        mensaje.innerHTML = '<li>El RUT ingresado es correcto.</li>';
        mensaje.style.color = "#28a745";
        if (variable == 1) {
            $("#estadorut_"+variable).val(1);
        }else{
            $("#estadorut_"+variable2).val(1);
        }
        return true;
    }
}

function format(rut) {
    rut = clean(rut)

    var result = rut.slice(-4, -1) + '-' + rut.substr(rut.length - 1)
    for (var i = 4; i < rut.length; i += 3) {
        result = rut.slice(-3 - i, -i) + '.' + result
    }

    return result
}

function clean(rut) {
    return typeof rut === 'string'
        ? rut.replace(/^0+|[^0-9kK]+/g, '').toUpperCase()
        : ''
}