"use strict";
var nombreMes = ["Enero", "Febrero", "Marzo", "Abril", "Mayo", "Junio", "Julio", "Agosto", "Septiembre", "Octubre", "Noviembre", "Diciembre"];

function numeroNombreMes(mes) {
  var numeroMes = parseInt(mes);
  if(! isNaN(numeroMes) && numeroMes >= 1  && numeroMes <= 12 ) {
      return  nombreMes[numeroMes - 1];
  }
}

function nombreANumero(mes){
    if(mes=='Enero'){
        return('01');
    }else if(mes=='Febrero'){
        return('02');
    }else if(mes=='Marzo'){
        return('03');
    }else if(mes=='Abril'){
        return('04');
    }else if(mes=='Mayo'){
        return('05');
    }else if(mes=='Junio'){
        return('06');
    }else if(mes=='Julio'){
        return('07');
    }else if(mes=='Agosto'){
        return('08');
    }else if(mes=='Septiembre'){
        return('09');
    }else if(mes=='Octubre'){
        return('10');
    }else if(mes=='Noviembre'){
        return('11');
    }else{
        return('12');
    }
}

function separadorMiles(n) {
    n = String(n).replace(/\D/g, "");
    return n === '' ? n : Number(n).toLocaleString();
}

var f = new Date();
var dia = f.getDate();
var mesActual =("0" + (f.getMonth() + 1)).slice(-2);
var mesAnterior =("0" + (f.getMonth())).slice(-2);
var mesAnio='';
var anioActual = f.getFullYear();

var ultimoDia = new Date(anioActual, mesAnterior, 0);

var fechaHoy = anioActual+'-'+mesActual+'-'+dia;
var fechaMesAnterior = anioActual+'-'+mesAnterior+'-'+ultimoDia.getDate()