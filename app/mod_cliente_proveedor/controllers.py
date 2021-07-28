#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, session, render_template, request, flash, redirect
from app import db, app, t
from app.mod_auth.controllers import getContribuyente, getDatosUsuario, CRut
from datetime import datetime
from datetime import timedelta
import sys
import requests

mod_cliente_proveedor = Blueprint('clienteProveedor', __name__, url_prefix='/clienteProveedor')


@mod_cliente_proveedor.route('/proveedores/<rut_contribuyente>', methods=['GET','POST','UPDATE'])
def proveedores(rut_contribuyente):
    if 'username' in session:
        cursor = db.cursor()
        titulo = 'Proveedores'
        anio_actual = t
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
        contribuyentes = cursor.fetchall()
        dtsUser = getContribuyente(datosUsx[0])
        cursor.execute("""select rut_cliente_proveedor,nombre_contribuyente,correo_contribuyente,desc_conf_contribuyente,conf_contribuyente.cod_cuenta from contribuyente,conf_contribuyente
         where cod_tipo_configuracion = 1 and rut_cliente_proveedor=contribuyente.rut_contribuyente and conf_contribuyente.rut_contribuyente = %s""",[rut_contribuyente])
        proveedores = cursor.fetchall()
        cursor.execute(
            "select distinct cuenta.cod_cuenta,cuenta.etiqueta from cuenta,role_cuenta where cod_role = 510000  and cuenta.cod_cuenta = role_cuenta.cod_cuenta ")
        cuentas = cursor.fetchall()
        if request.method == "UPDATE":
            try:
                if request.content_type == 'application/json':
                    data = request.json
                    cursor.execute(
                        "update contribuyente set correo_contribuyente=%(correo_contribuyente)s where rut_contribuyente=%(rut_cliente_proveedor)s",
                        data)
                    cursor.execute("update conf_contribuyente set desc_conf_contribuyente=%(desc_conf_contribuyente)s, cod_cuenta=%(cod_cuenta)s where rut_cliente_proveedor=%(rut_cliente_proveedor)s and rut_contribuyente=%(rut_contribuyente)s",data)
                    db.commit()
                    mensaje = 'ok'
                    flash(mensaje)
            except:
                mensaje = 'error'
                flash(mensaje)
                db.rollback()
                print("error no esperado", sys.exc_info())
        return render_template('/clienteProveedor/proveedores.html', proveedores=proveedores,
                               anio_actual=anio_actual, datosUsx=datosUsx, contribuyentes=contribuyentes,titulo=titulo,dtsUser=dtsUser,cuentas=cuentas)
    return redirect('/auth/login')


@mod_cliente_proveedor.route('/clientes/<rut_contribuyente>', methods=['GET','POST','UPDATE'])
def clientes(rut_contribuyente):
    if 'username' in session:
        cursor = db.cursor()
        titulo = 'clientes'
        anio_actual = t
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
        contribuyentes = cursor.fetchall()
        dtsUser = getContribuyente(datosUsx[0])
        cursor.execute("""select rut_cliente_proveedor,nombre_contribuyente,correo_contribuyente,desc_conf_contribuyente,conf_contribuyente.cod_cuenta from contribuyente,conf_contribuyente
                 where cod_tipo_configuracion = 2 and rut_cliente_proveedor=contribuyente.rut_contribuyente and conf_contribuyente.rut_contribuyente = %s""",
                       [rut_contribuyente])
        clientes = cursor.fetchall()
        cursor.execute("select distinct cuenta.cod_cuenta,cuenta.etiqueta from cuenta,role_cuenta where cod_role = 510000  and cuenta.cod_cuenta = role_cuenta.cod_cuenta ")
        cuentas = cursor.fetchall()
        if request.method == "UPDATE":
            try:
                if request.content_type == 'application/json':
                    data = request.json
                    cursor.execute(
                        "update contribuyente set correo_contribuyente=%(correo_contribuyente)s where rut_contribuyente=%(rut_cliente_proveedor)s",
                        data)
                    cursor.execute(
                        "update conf_contribuyente set desc_conf_contribuyente=%(desc_conf_contribuyente)s, cod_cuenta=%(cod_cuenta)s where rut_cliente_proveedor=%(rut_cliente_proveedor)s and rut_contribuyente=%(rut_contribuyente)s",
                        data)
                    db.commit()
                    mensaje = 'ok'
                    flash(mensaje)
            except:
                mensaje = 'error'
                flash(mensaje)
                db.rollback()
                print("error no esperado", sys.exc_info())
        return render_template('/clienteProveedor/clientes.html', clientes=clientes,
                               anio_actual=anio_actual, datosUsx=datosUsx, contribuyentes=contribuyentes,titulo=titulo,dtsUser=dtsUser,cuentas=cuentas)
    return redirect('/auth/login')