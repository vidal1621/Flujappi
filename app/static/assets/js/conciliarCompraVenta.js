$('#fechaVista').datepicker({
    viewMode: 'years',
    format: 'mm-yyyy',
    startView: "months",
    minViewMode: "months"
});
var startDate = new Date('2021-01-01'); // Now
var endDate = new Date(fechaHoy);
$('.fechaVista').datepicker('setEndDate', endDate);//1st set  end date
$('.fechaVista').datepicker('setStartDate', startDate);//

 $('.fechaVista').val(mesActual + '-' + anioActual);
fecha();
function fecha() {
    var fecha = $('#fechaVista').val().split('-');
    $("#mes").val(fecha[0]);
    $("#anio").val(fecha[1]);
}

function conciliar(folio,rut,cliente,fechaEmision,fechaVcto,monto,estado,descMovimiento,fechaMovimiento,montoMovimiento){
    if(estado=='conciliada'){
        $('#modalConciliada').modal('show');
        /*$("#folio").val(folio);*/
        $("#descripcionMovimientoConciliada").html(descMovimiento);
        $("#fechaMovimientoConciliada").html(fechaMovimiento);
        $("#montoMovimientoConciliada").html(montoMovimiento+ ' <span class="currency currency-usd">CLP</span>');
        $("#rutConciliada").html(rut + ' ' + cliente);
        $("#fechaEmisionConciliada").html(fechaEmision);
        $("#fechaVctoConciliada").html(fechaVcto);
        $("#montoConciliada").html(separadorMiles(monto) + ' <span class="currency currency-usd">CLP</span>');
    }else {
        $('#modalConciliar').modal('show');
        $("#folio").val(folio);
        $("#rut").html(rut + ' ' + cliente);
        $("#fechaEmision").html(fechaEmision);
        $("#fechaVcto").html(fechaVcto);
        $("#monto").html(separadorMiles(monto) + ' <span class="currency currency-usd">CLP</span>');
        $("#descripcionConciliacion").val(rut + ' ' + cliente);
        $("#totalCompraVenta").val(monto);
        var totalS = $("#totalCompraVenta").val().replace(',', '');
        movimientoBancarioSugerido(totalS);
    }
}

function movimientoBancarioSugerido(totalS){
    $('#ejemplito').DataTable().rows().iterator('row', function(context, index){
        var valor = parseInt(this.row(index).node().children[0].children[0].value)
        /*console.log(valor+'    '+totalS)*/
        if(parseInt(totalS)==valor){
             var id = 'sugerenciaMostrar_43';
                    $("#"+id).html("<img src='/static/assets/gif/sugerencia.gif' style='width: 25px;background: #1ee0ac;border-radius: 50%'>")
                   /* var colorFila = id.split('_');
                    document.getElementById('fila_'+colorFila[1]).style.backgroundColor = "darkslategrey";*/

            $(".sugerenciaMostrar"+valor).each(function (i) {
                console.log('11')
                    /*console.log($(".sugerenciaMostrar"+valor)[i].getAttribute('id'))*/

                });

            $('.sugerenciaMostrar'+valor).each(function(){
              /*var elemento = document.getElementsByClassName('sugerenciaMostrar'+valor);*/

                console.log(this.attr('id'))
            });


            /*var id = elemento[0].getAttribute('id');
            $("#"+id).html("<img src='/static/assets/gif/sugerencia.gif' style='width: 25px;background: #1ee0ac;border-radius: 50%'>")
            var colorFila = id.split('_');
            document.getElementById('fila_'+colorFila[1]).style.backgroundColor = "darkslategrey";*/
        }
    });
    /*setTimeout(movimientoBancarioSugerido(totalS),5000)*/
}

function movimientoBancario(codigoMovimiento,descripcionMovimiento,fechaMovimiento,montoMovimiento, contador){
    $("#descripcionMovimiento").html(descripcionMovimiento);
    $("#fechaMovimiento").html(fechaMovimiento);
    $("#montoMovimiento").html(separadorMiles(montoMovimiento));
    $("#codigoMovimiento").val(codigoMovimiento);
    $("#totalMovimientoBancario").val(montoMovimiento);
    var montoRestante = montoMovimiento.replace(',','') - parseInt($("#totalCompraVenta").val().replace(',',''));
    console.log(montoRestante)
    if(montoMovimiento.replace(',','')<=parseInt($("#totalCompraVenta").val().replace(',',''))){
        $("#montoRestante").html('0 <span class="currency currency-usd">CLP</span>')
    }else{
        $("#montoRestante").html(separadorMiles(montoRestante)+' <span class="currency currency-usd">CLP</span>')
    }

    $("#contadorFila").val(contador);
    if(descripcionMovimiento!=''){
        $("#btnConciliar").show();
    }else{
        $("#btnConciliar").hide();
    }
}

function agregarConciliacion(modelo){
    if($("#codigoMovimiento").val()==''){
        Swal.fire("Alerta", "Debe ingresar un movimiento bancario", "warning");
    }else if($("#folio").val()=='') {
        Swal.fire("Alerta", "Debe seleccionar una compra", "warning");
    }else {
        $.ajax({
            type: "post",
            url: '/'+modelo+'/conciliacion/'+$("#descripcionConciliacion").val()+'/'+$("#codigoMovimiento").val()+'/'+$("#folio").val()+'/'+$("#totalCompraVenta").val()+'/'+$("#totalMovimientoBancario").val(),
            success: function (respuesta) {
                Swal.fire("Correcto", "Se realizó la conciliación correctamente", "success");
                $("#btnConciliar").hide();
                setTimeout('document.location.reload()', 3000);
            },
            error: function () {
                alert('Disculpe, existió un problema');
            }
        })
    }
}

function limpiarDatos(){
    $("#descripcionMovimiento").html('');
    $("#fechaMovimiento").html('');
    $("#montoMovimiento").html('');
    $("#codigoMovimiento").val('');
    $("#btnConciliar").hide();
    $("#codigoMovimiento").val('');
    $("#totalMovimientoBancario").val('');
    $("#descripcionConciliacion").val('');
    $("#totalCompraVenta").val('');
    $("#montoRestante").html('')
}

function solicitudActualizarCompraVenta(modelo){
    fecha();
    if($("#fechaVista").val()!=''){
        $.ajax({
            type: "post",
            url: '/'+modelo+'/solicitudes/'+$("#rutContribuyente").val()+'/0/'+$("#mes").val()+'/'+$("#anio").val()+'/procesando',
            success: function (respuesta) {
                console.log(respuesta);
                Swal.fire("Alerta", "Se envió la solicitud para actualizar sus datos, esto puede tardar unos minutos", "info");
                $("#btn_actualizar").hide();
                setTimeout('document.location.reload()', 3000);
            },
            error: function () {
                 Swal.fire("Error", "Disculpe, existió un problema", "error");
            }
        })
    }else{
        Swal.fire("Error", "Debe ingresar una fecha para actualizar los datos", "warning");
    }
}