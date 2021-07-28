#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, session, render_template, request, flash, redirect
from app import db, app, t
from app.mod_auth.controllers import getContribuyente, getDatosUsuario, CRut
from datetime import datetime
from datetime import timedelta
import sys
import requests

mod_reporte = Blueprint('reporte', __name__, url_prefix='/reporte')


@mod_reporte.route('/registroConciliacion/<rut_contribuyente>', methods=['GET', 'POST'])
def registroConciliacion(rut_contribuyente):
    if 'username' in session:
        cursor = db.cursor()
        titulo = 'Reporte Conciliacion'
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
        contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        dtsUser = getContribuyente(cod_usuario[0])
        cursor.execute("""select DISTINCT registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                    fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                    ,conciliacion.cod_movimiento_cb,desc_registro_cv ,desc_movimiento_cb,fecha_movimiento,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                    from registro_cv,contribuyente,conf_contribuyente,conciliacion,movimiento_cb where 
                        emisor=%s and contribuyente.rut_contribuyente=receptor 
                        and receptor = rut_cliente_proveedor and conciliacion.cod_registro_cv=registro_cv.cod_registro_cv 
                        and movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb 
                        group by registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                    fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                    ,conciliacion.cod_movimiento_cb,desc_movimiento_cb,fecha_movimiento
        """,[rut_contribuyente])
        conciliacionesVenta = cursor.fetchall()
        cursor.execute("""select DISTINCT registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                                fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                                ,conciliacion.cod_movimiento_cb,desc_registro_cv ,desc_movimiento_cb,fecha_movimiento,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                from registro_cv,contribuyente,conf_contribuyente,conciliacion,movimiento_cb where 
                                    receptor=%s and contribuyente.rut_contribuyente=emisor 
                                    and emisor = rut_cliente_proveedor and conciliacion.cod_registro_cv=registro_cv.cod_registro_cv 
                                    and movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb 
                                    group by registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                                fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                                ,conciliacion.cod_movimiento_cb,desc_movimiento_cb,fecha_movimiento""",
                       [rut_contribuyente])
        conciliacionesCompra = cursor.fetchall()
        return render_template("/reportes/registroConciliacion.html",titulo=titulo,conciliacionesVenta=conciliacionesVenta,conciliacionesCompra=conciliacionesCompra,datosUsx=datosUsx
                               ,dtsUser=dtsUser,rut_contribuyente=rut_contribuyente,contribuyentes=contribuyentes)
    return redirect('/auth/login')
