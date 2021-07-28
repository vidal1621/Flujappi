$('#fechaVista').datepicker({
    viewMode: 'years',
    format: 'mm-yyyy',
    startView: "months",
    minViewMode: "months"
});

if(banco=='bci'){
    f.setMonth(f.getMonth() - 3)
    var startDate = new Date(f.getFullYear() +"-"+ (f.getMonth()+1) +"-"+ f.getDate()); // Now

}else if(banco=='estado'){
    var startDate = new Date('2021-02-01'); // Now
}else if(banco=='chile'){
    var startDate = new Date('2021-01-01'); // Now
}else{
    var startDate = new Date('2018-02-01'); // Now
}
var endDate = new Date(fechaMesAnterior);

$('.fechaVista').datepicker('setEndDate', endDate);//1st set  end date
$('.fechaVista').datepicker('setStartDate', startDate);//
$('.fechaVista').val(mesAnterior + '-' + anioActual);
$("#mes").val(numeroNombreMes(mesAnterior));

fecha();
function fecha() {
    var fecha = $('#fechaVista').val().split('-');
    $("#mes").val(numeroNombreMes(fecha[0]));
    $("#anio").val(fecha[1]);

    if(banco=='estado') {
        var ultimoDia = new Date(fecha[1], fecha[0], 0);
        $("#inicio").val('01' + fecha[0] + fecha[1]);
        $("#fin").val(ultimoDia.getDate() + fecha[0] + fecha[1]);
    }

    if(banco=='chile') {
        var ultimoDia = new Date(fecha[1], fecha[0], 0);
        $("#inicio").val('01' +'/'+fecha[0]+'/'+fecha[1]);
        $("#fin").val(ultimoDia.getDate() +'/'+fecha[0]+'/'+fecha[1]);
    }
}

function conciliar(idMovimiento,descripcion,fecha,cargo,abono,estado,rut,descripcionConciliada,fechaEmsion,fechaVcto,montoTotal){
    var monto = parseInt(cargo) + parseInt(abono);
    if(estado=='conciliada'){
         $('#modalConciliada').modal('show');
        /*$("#folio").val(folio);*/
         $("#descripcionMovimientoConciliado").html(descripcion);
        $("#fechaMovimientoConciliado").html(fecha);
        $("#montoMovimientoConciliado").html(separadorMiles(monto) + ' <span class="currency currency-usd">CLP</span>');

        $("#rutConciliado").html(rut + ' ' + descripcionConciliada);
        $("#fechaEmisionConciliado").html(fechaEmsion);
        $("#fechaVctoConciliado").html(fechaVcto);
        $("#montoConciliado2").html(separadorMiles(montoTotal) + ' <span class="currency currency-usd">CLP</span>');
    }else {
        $('#modalConciliar').modal('show');
        $("#codigoMovimiento").val(idMovimiento);
        $("#descripcionMovimiento").html(descripcion);
        $("#fechaMovimiento").html(fecha);
        $("#montoMovimiento").html(separadorMiles(monto) + ' <span class="currency currency-usd">CLP</span>');
        $("#totalMovimientoBancario").val(monto)
        $("#descripcionConciliacion").val(descripcion);
        movimientoCompraVentaSugerido(monto);
    }
}

function movimientoCompraVentaSugerido(totalS){
    $(".totalMovimientoCompraVentaSugerido").each(function (i) {
        var valor = parseInt($(".totalMovimientoCompraVentaSugerido")[i].value || 0);
        if(totalS==valor){
            var elemento = document.getElementsByClassName('sugerenciaMostrar'+valor);
            var id = elemento[0].getAttribute('id');
            $("#"+id).html("<img src='/static/assets/gif/sugerencia.gif' style='width: 25px;background: #1ee0ac;border-radius: 50%'>")
            var colorFila = id.split('_');
            console.log(id)
            document.getElementById('fila_'+colorFila[1]).style.backgroundColor = "darkslategrey";
        }
    });
}

function movimientoCompraVenta(folio,rut,cliente,fechaEmision, fechaVcto,monto,contador){
    $("#folio").val(folio);
    $("#rut").html(rut+' '+cliente);
    $("#fechaEmision").html(fechaEmision);
    $("#fechaVcto").html(fechaVcto);
    $("#monto").html(separadorMiles(monto)+' <span class="currency currency-usd">CLP</span>');
    $("#totalCompraVenta").val(monto);
    var montoRestante = $("#totalMovimientoBancario").val().replace(',','') - parseInt($("#totalCompraVenta").val().replace(',',''));
    if($("#totalMovimientoBancario").val().replace(',','')<=parseInt($("#totalCompraVenta").val().replace(',',''))){
        $("#montoRestante").html('0 <span class="currency currency-usd">CLP</span>')
    }else{
        $("#montoRestante").html(separadorMiles(montoRestante)+' <span class="currency currency-usd">CLP</span>')
    }
    $("#contadorFila").val(contador);
    if($("#descripcionConciliacion").val()!=''){
        $("#btnConciliar").show();
    }else{
        $("#btnConciliar").hide();
    }
}

function agregarConciliacion(){
    if($("#codigoMovimiento").val()==''){
        Swal.fire("Alerta", "Debe ingresar un movimiento bancario", "warning");
    }else if($("#folio").val()=='') {
        Swal.fire("Alerta", "Debe seleccionar una compra", "warning");
    }else {
        $.ajax({
            type: "post",
            url: '/bancos/conciliacion/'+$("#descripcionConciliacion").val()+'/'+$("#codigoMovimiento").val()+'/'+$("#folio").val()+'/'+$("#totalCompraVenta").val()+'/'+$("#totalMovimientoBancario").val(),
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
    $("#rut").html('');
    $("#fechaEmision").html('');
    $("#fechaVcto").html('');
    $("#monto").html('');
    $("#folio").val('');
    $("#totalCompraVenta").val('');
    $("#btnConciliar").hide();
}

function solicitudActualizarBanco(){
    fecha();
    /*alert('/bancos/solicitudes/'+$("#rutApoderado").val()+'/'+ $("#cuentaBancaria").val()+'/'+$("#mes").val()+'/'+$("#anio").val()+'/procesando');*/
    if($("#fechaVista").val()!=''){
        $.ajax({
            type: "post",
            url: '/bancos/solicitudes/'+$("#rutApoderado").val()+'/'+ $("#cuentaBancaria").val()+'/'+$("#mes").val()+'/'+$("#anio").val()+'/procesando/'+$("#cod_Banco").val()+'/'+$("#inicio").val()+'/'+$("#fin").val(),
            success: function (respuesta) {
                console.log(respuesta)
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