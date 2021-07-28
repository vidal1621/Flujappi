#!/usr/bin/env python
# -*- coding: utf-8 -*-
from flask import Blueprint, session, render_template, request, flash, redirect
from app import db, app, t
from app.mod_auth.controllers import getContribuyente, getDatosUsuario, CRut
from datetime import datetime
from datetime import timedelta
import sys
import requests

mod_compra = Blueprint('compra', __name__, url_prefix='/compra')


def actualizarCompras(rut_contribuyente,anio,mes):
    cursor = db.cursor()
    cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
    contribuyentes = cursor.fetchall()
    rutCV = contribuyentes[0][0]
    dv = rutCV.split(sep='-', maxsplit=2)
    rutSV = dv[0].replace('.', '')
    digitoVerificador = dv[1]
    cursor.execute("select clave_tributaria from contribuyente where rut_contribuyente=%s", [rut_contribuyente])
    contrasena = cursor.fetchone()[0]

    periodo = anio + mes
    urlCompras = "http://dte2.xdte.cl:1528/get_compras"
    # payload = {"\"rut\":\"rut\",\"dv\":\"dvr\",\"pas\":\"clave\",\"periodo\":\"periodo\""}
    payload = '{"rut":"%s","dv":"%s","pas":"%s","periodo":"%s"}' % (
        rutSV, digitoVerificador, contrasena, periodo)

    headers = {
        'Content-Type': 'application/json'
    }
    response = requests.request("GET", urlCompras, headers=headers, data=payload)
    if response.status_code == 500:
        print("error en API")
    data = response.json()
    try:
        if data:

            for d in range(len(data['REGISTRO'])):
                dte = data['REGISTRO'][d]['dte']
                receptor = CRut(data['REGISTRO'][d]['emisor'])
                fecha = data['REGISTRO'][d]['fecha']
                iva = data['REGISTRO'][d]['iva']
                neto = data['REGISTRO'][d]['neto']
                total = data['REGISTRO'][d]['total']
                exento = data['REGISTRO'][d]['exento']
                folio = data['REGISTRO'][d]['Folio']
                razon_social = data['REGISTRO'][d]['razonSocial']
                cod_entidad = rutCV
                estado_documento = 'no conciliada'

                cursor.execute(
                    "select desc_conf_contribuyente from conf_contribuyente where rut_contribuyente=%s and rut_cliente_proveedor=%s and cod_tipo_configuracion=%s",
                    [rutCV, receptor, 1])
                conf_contribuyente = cursor.fetchone()
                fecha_modificada = datetime.strptime(fecha, '%d/%m/%Y')
                cursor.execute(
                    "select rut_contribuyente,nombre_contribuyente from contribuyente where rut_contribuyente =%s",
                    [receptor])
                ncontribuyente = cursor.fetchone()
                try:
                    cursor.execute("select cod_registro_cv from registro_cv where cod_registro_cv=%s", [folio])
                    exist_folio = cursor.fetchone()
                except:
                    db.rollback()
                    print("error no esperado", sys.exc_info())
                if not exist_folio:
                    if not ncontribuyente:
                        try:
                            dias = 30
                            cursor.execute(
                                "insert into contribuyente (rut_contribuyente,nombre_contribuyente) values(%s,%s)",
                                [receptor, razon_social])
                            cursor.execute("""insert into conf_contribuyente (desc_conf_contribuyente,rut_contribuyente,rut_cliente_proveedor,cod_tipo_configuracion,cod_cuenta)values 
                                                                                   (%s,%s,%s,%s,%s)""",
                                           [dias, rut_contribuyente, receptor, 1,586])
                            db.commit()
                        except:
                            db.rollback()
                            print("error no esperado", sys.exc_info())
                    if conf_contribuyente:
                        dias_cobro = int(conf_contribuyente[0])
                        fecha_vencimiento = fecha_modificada + timedelta(days=dias_cobro)
                        cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                                        monto_iva,monto_total,saldo_documento,estado_documento)
                                                                             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                       [folio, dias_cobro, dte, cod_entidad, receptor, fecha_modificada,
                                        fecha_vencimiento,
                                        neto or 0,
                                        exento or 0, iva or 0,
                                        total or 0, total or 0, estado_documento])
                    else:
                        dias = int(conf_contribuyente[0])
                        fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                        cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                    monto_iva,monto_total,saldo_documento,estado_documento)
                                                         values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                       [folio, dias, dte, cod_entidad, receptor, fecha_modificada,
                                        fecha_vencimiento,
                                        neto or 0,
                                        exento or 0, iva or 0,
                                        total or 0, total or 0, estado_documento])

                else:
                    print("folio existe")
                    try:
                        dias = int(conf_contribuyente[0])
                        fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                        cursor.execute("update registro_cv set fecha_vencimiento=%s where  cod_registro_cv=%s",
                                       [fecha_vencimiento, folio])
                    except:
                        db.rollback()
                        print("error no esperado", sys.exc_info())
            print("compras guardadas con exito")
            db.commit()
            success = 'actualizado'
            flash(success)
    except:
        db.rollback()
        print("error no esperado", sys.exc_info())
        error = 'error'
        flash(error)
        return error

    success = 'actualizado'
    flash(success)
    return success


@mod_compra.route('/solicitudes/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>/<estado>',methods=['GET', 'POST'])
def solicitudes(rut_contribuyente,tipo_cuenta,mes,anio,estado):
    cursor = db.cursor()
    desc_cartola = mes + '-' + anio
    if estado == 'procesando':
        try:
            cursor.execute("insert into solicitudes (desc_solicitudes,estado,rut_contribuyente,cod_tipo_cuenta,desc_cartola,anio,mes) values (%s,%s,%s,%s,%s,%s,%s)",['compras',estado,rut_contribuyente,tipo_cuenta,desc_cartola,anio,mes])
            db.commit()
            respuesta = 'ok'
            return respuesta
        except:
            db.rollback()
            print("error no esperado", sys.exc_info())
            respuesta = 'error'
            return respuesta
    else:
        try:
            cursor.execute("""update solicitudes set estado=%s
            where desc_cartola=%s and anio=%s and mes=%s and desc_solicitudes='compras'"""
                           ,[estado,desc_cartola,anio,mes])
            db.commit()
            respuesta = 'ok'
            return respuesta
        except:
            db.rollback()
            print("error no esperado", sys.exc_info())
            respuesta = 'error'
            return respuesta


@mod_compra.route('/conciliacion/<desc_conciliacion>/<cod_movimiento_cb>/<cod_registro_cv>/<monto_sii>/<monto_banco>',
                  methods=['GET', 'POST'])
def conciliacion(desc_conciliacion, cod_movimiento_cb, cod_registro_cv, monto_sii, monto_banco):
    cursor = db.cursor()
    monto_banco = int(monto_banco.replace(",", ""))
    monto_sii = int(monto_sii.replace(",", ""))
    conciliacion = monto_sii - monto_banco
    try:
        cursor.execute(
            """insert into conciliacion (desc_conciliacion,cod_movimiento_cb,cod_registro_cv,monto_conciliacion)values (%s,%s,%s,%s)"""
            , [desc_conciliacion, cod_movimiento_cb, cod_registro_cv, conciliacion])
        cursor.execute("update registro_cv set estado_documento='conciliada' where cod_registro_cv=%s",
                       [cod_registro_cv])
        cursor.execute("update movimiento_cb set estado_bancaria='conciliada' where cod_movimiento_cb=%s",
                       [cod_movimiento_cb])
        db.commit()
        return "ok"
    except:
        db.rollback()
        print("error no esperado", sys.exc_info())
        return "error"


@mod_compra.route('/registroCompras/<rut_contribuyente>', methods=['GET', 'POST'])
def registroCompras(rut_contribuyente):

    date = datetime.now()
    year_month = date.strftime('%Y%m')
    # year_month = '202101'
    month = date.strftime('%m')
    datosUsx = getDatosUsuario(session['username'])
    cursor = db.cursor()

    cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
    cod_usuario = cursor.fetchone()
    if cod_usuario:
        cod_usuario = cod_usuario[0]
    else:
        cod_usuario = cod_usuario
    dtsUser = getContribuyente(cod_usuario)
    cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
    contribuyentes = cursor.fetchall()
    rutCV = contribuyentes[0][0]

    dv = rutCV.split(sep='-', maxsplit=2)
    rutSV = dv[0].replace('.', '')
    digitoVerificador = dv[1]
    cursor.execute("select clave_tributaria from contribuyente where rut_contribuyente=%s", [rut_contribuyente])
    contrasena = cursor.fetchone()[0]
    titulo = 'Registro Compras'
    anio_actual = t
    cursor.execute(
        "select DISTINCT cod_registro_cv,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,estado_documento from registro_cv,contribuyente,conf_contribuyente where receptor=%s and contribuyente.rut_contribuyente=emisor and emisor = rut_cliente_proveedor ",
        [rut_contribuyente])
    cprs = cursor.fetchall()
    cursor.execute("""select DISTINCT registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                        fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                        ,conciliacion.cod_movimiento_cb,desc_registro_cv ,desc_movimiento_cb,fecha_movimiento,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                        from registro_cv,contribuyente,conf_contribuyente,conciliacion,movimiento_cb where 
                            receptor=%s and contribuyente.rut_contribuyente=emisor 
                            and emisor = rut_cliente_proveedor and conciliacion.cod_registro_cv=registro_cv.cod_registro_cv 
                            and movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb 
                            group by registro_cv.cod_registro_cv,emisor,receptor,fecha_emision,
                        fecha_vencimiento,monto_total,correo_contribuyente,nombre_contribuyente,desc_conf_contribuyente,monto_conciliacion
                        ,conciliacion.cod_movimiento_cb,desc_movimiento_cb,fecha_movimiento""", [rut_contribuyente])
    conciliacionesCompra = cursor.fetchall()
    cursor.execute(
        "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s  ",
        [rut_contribuyente])
    clientesUnicosComprasAnuales = cursor.fetchone()
    cursor.execute(
        "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s and EXTRACT(MONTH FROM fecha_emision) = extract(month from now()) ",
        [rut_contribuyente])
    clientesUnicosComprasMensuales = cursor.fetchone()
    graficoCantidades = []
    graficoCount = []
    cursor.execute(
        """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s """,
        [rut_contribuyente, rut_contribuyente])
    ctaBancaria = cursor.fetchone()
    cursor.execute("select cod_cartola_bancaria from cartola_bancaria where cod_cuenta_bancaria=%s", [ctaBancaria[0]])
    ncartola = cursor.fetchall()
    mobs = []
    for n in range(len(list(ncartola))):
        cursor.execute(
            "select cod_movimiento_cb,desc_movimiento_cb,cod_cuenta_bancaria,num_documento,cargo,abono,fecha_movimiento,cod_cartola_bancaria,estado_bancaria from movimiento_cb where cod_cartola_bancaria=%s order by desc_movimiento_cb asc",
            [ncartola[n]])
        movimiento_cb = cursor.fetchall()
        mobs.append(movimiento_cb)
    if request.method == "POST":
        anio = request.form["anio"]
        mes = request.form["mes"]
        periodo = anio + mes

        cursor.execute("select count(desc_registro_cv) from registro_cv where receptor = %s", [rutCV])
        cantidadTotalAnual = cursor.fetchone()
        cursor.execute("select sum(monto_total) from registro_cv where receptor = %s", [rutCV])
        totalCompras = cursor.fetchone()
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,count(desc_registro_cv) from registro_cv where receptor = %s and 
                                            extract(year from now())=EXTRACT(year FROM fecha_emision)
                                            GROUP BY mes,anio order by mes asc""", [rutCV])
        ventasCount = cursor.fetchall()
        for v in range(len(list(ventasCount))):
            objGraficoCount = {
                'anio': int(ventasCount[v][1]),
                'mes': int(ventasCount[v][0]),
                'cantidad': int(ventasCount[v][-1])
            }

            graficoCount.append(objGraficoCount)
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,sum(monto_total) from registro_cv where receptor = %s and 
                                            extract(year from now())=EXTRACT(year FROM fecha_emision)
                                            GROUP BY mes,anio order by mes asc""", [rutCV])
        ventasGrafico = cursor.fetchall()
        for v in range(len(list(ventasGrafico))):
            objGraficoCantidades = {
                'anio': int(ventasGrafico[v][1]),
                'mes': int(ventasGrafico[v][0]),
                'cantidad': int(ventasGrafico[v][-1])
            }

            graficoCantidades.append(objGraficoCantidades)

        urlCompras = "http://dte2.xdte.cl:1528/get_compras"
        # payload = {"\"rut\":\"rut\",\"dv\":\"dvr\",\"pas\":\"clave\",\"periodo\":\"periodo\""}
        payload = '{"rut":"%s","dv":"%s","pas":"%s","periodo":"%s"}' % (
            rutSV, digitoVerificador, contrasena, periodo)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", urlCompras, headers=headers, data=payload)
        if response.status_code == 500:
            print("error en API")
        data = response.json()
        try:
            if data:

                for d in range(len(data['REGISTRO'])):
                    dte = data['REGISTRO'][d]['dte']
                    receptor = CRut(data['REGISTRO'][d]['emisor'])
                    fecha = data['REGISTRO'][d]['fecha']
                    iva = data['REGISTRO'][d]['iva']
                    neto = data['REGISTRO'][d]['neto']
                    total = data['REGISTRO'][d]['total']
                    exento = data['REGISTRO'][d]['exento']
                    folio = data['REGISTRO'][d]['Folio']
                    razon_social = data['REGISTRO'][d]['razonSocial']
                    cod_entidad = rutCV
                    estado_documento = 'no conciliada'

                    cursor.execute(
                        "select desc_conf_contribuyente from conf_contribuyente where rut_contribuyente=%s and rut_cliente_proveedor=%s and cod_tipo_configuracion=%s",
                        [rutCV, receptor, 1])
                    conf_contribuyente = cursor.fetchone()
                    fecha_modificada = datetime.strptime(fecha, '%d/%m/%Y')
                    cursor.execute(
                        "select rut_contribuyente,nombre_contribuyente from contribuyente where rut_contribuyente =%s",
                        [receptor])
                    ncontribuyente = cursor.fetchone()
                    try:
                        cursor.execute("select cod_registro_cv from registro_cv where cod_registro_cv=%s", [folio])
                        exist_folio = cursor.fetchone()
                    except:
                        db.rollback()
                        print("error no esperado", sys.exc_info())
                    if not exist_folio:
                        if not ncontribuyente:
                            try:
                                dias = 30
                                cursor.execute(
                                    "insert into contribuyente (rut_contribuyente,nombre_contribuyente) values(%s,%s)",
                                    [receptor, razon_social])
                                cursor.execute("""insert into conf_contribuyente (desc_conf_contribuyente,rut_contribuyente,rut_cliente_proveedor,cod_tipo_configuracion)values 
                                                                                       (%s,%s,%s,%s)""",
                                               [dias, rut_contribuyente, receptor, 1])
                                db.commit()
                            except:
                                db.rollback()
                                print("error no esperado", sys.exc_info())
                        if conf_contribuyente:
                            dias_cobro = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias_cobro)
                            cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                                            monto_iva,monto_total,saldo_documento,estado_documento)
                                                                                 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                           [folio, dias_cobro, dte, cod_entidad, receptor, fecha_modificada,
                                            fecha_vencimiento,
                                            neto or 0,
                                            exento or 0, iva or 0,
                                            total or 0, total or 0, estado_documento])
                        else:
                            dias = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                            cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                        monto_iva,monto_total,saldo_documento,estado_documento)
                                                             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                           [folio, dias, dte, cod_entidad, receptor, fecha_modificada,
                                            fecha_vencimiento,
                                            neto or 0,
                                            exento or 0, iva or 0,
                                            total or 0, total or 0, estado_documento])

                    else:
                        print("folio existe")
                        try:
                            dias = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                            cursor.execute("update registro_cv set fecha_vencimiento=%s where  cod_registro_cv=%s",
                                           [fecha_vencimiento, folio])
                        except:
                            db.rollback()
                            print("error no esperado", sys.exc_info())
                print("compras guardadas con exito")
                db.commit()
                success = 'actualizado'
                flash(success)
        except:
            db.rollback()
            print("error no esperado", sys.exc_info())
            return render_template('/egresos/Compras.html', titulo=titulo, anio_actual=anio_actual,
                                   datosUsx=datosUsx,contribuyentes=contribuyentes, dtsUser=dtsUser)
        return render_template('/egresos/Compras.html', titulo=titulo, anio_actual=anio_actual,
                               datosUsx=datosUsx, cprs=cprs, graficoCantidades=graficoCantidades,
                               graficoCount=graficoCount, clientesUnicosComprasAnuales=clientesUnicosComprasAnuales,
                               clientesUnicosComprasMensuales=clientesUnicosComprasMensuales,
                               totalCompras=totalCompras, cantidadTotalAnual=cantidadTotalAnual,
                               contribuyentes=contribuyentes, dtsUser=dtsUser, mobs=mobs,
                               conciliacionesCompra=conciliacionesCompra)
    if cprs:
        cursor.execute(
            "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s  ",
            [rut_contribuyente])
        clientesUnicosComprasAnuales = cursor.fetchone()
        cursor.execute(
            "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s and EXTRACT(MONTH FROM fecha_emision) = extract(month from now()) ",
            [rut_contribuyente])
        clientesUnicosComprasMensuales = cursor.fetchone()
        cursor.execute("select count(desc_registro_cv) from registro_cv where receptor = %s", [rutCV])
        cantidadTotalAnual = cursor.fetchone()
        cursor.execute("select sum(monto_total) from registro_cv where receptor = %s", [rutCV])
        totalCompras = cursor.fetchone()
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,count(desc_registro_cv) from registro_cv where receptor = %s and 
                                    extract(year from now())=EXTRACT(year FROM fecha_emision)
                                    GROUP BY mes,anio order by mes asc""", [rutCV])
        ventasCount = cursor.fetchall()
        for v in range(len(list(ventasCount))):
            objGraficoCount = {
                'anio': int(ventasCount[v][1]),
                'mes': int(ventasCount[v][0]),
                'cantidad': int(ventasCount[v][-1])
            }

            graficoCount.append(objGraficoCount)
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,sum(monto_total) from registro_cv where receptor = %s and 
                                    extract(year from now())=EXTRACT(year FROM fecha_emision)
                                    GROUP BY mes,anio order by mes asc""", [rutCV])
        ventasGrafico = cursor.fetchall()
        for v in range(len(list(ventasGrafico))):
            objGraficoCantidades = {
                'anio': int(ventasGrafico[v][1]),
                'mes': int(ventasGrafico[v][0]),
                'cantidad': int(ventasGrafico[v][-1])
            }

            graficoCantidades.append(objGraficoCantidades)
        cursor.execute("""select to_char(fecha_emision, 'yyyy') as año,to_char(fecha_emision , 'dd')as dia,sum(monto_total)total from registro_cv where receptor=%s
                                    group by año,dia order by dia asc""", [rut_contribuyente])
        graficoComprasDias = cursor.fetchall()
        return render_template('/egresos/Compras.html', titulo=titulo, anio_actual=anio_actual,
                               datosUsx=datosUsx, cprs=cprs, graficoCantidades=graficoCantidades,
                               graficoCount=graficoCount, clientesUnicosComprasMensuales=clientesUnicosComprasMensuales,
                               clientesUnicosComprasAnuales=clientesUnicosComprasAnuales,
                               totalCompras=totalCompras, cantidadTotalAnual=cantidadTotalAnual,
                               contribuyentes=contribuyentes, dtsUser=dtsUser, mobs=mobs,
                               conciliacionesCompra=conciliacionesCompra,graficoComprasDias=graficoComprasDias)
    else:
        urlCompras = "http://dte2.xdte.cl:1528/get_compras"
        # payload = {"\"rut\":\"rut\",\"dv\":\"dvr\",\"pas\":\"clave\",\"periodo\":\"periodo\""}
        payload = '{"rut":"%s","dv":"%s","pas":"%s","periodo":"%s"}' % (
            rutSV, digitoVerificador, contrasena, year_month)

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", urlCompras, headers=headers, data=payload)
        if response.status_code == 500:
            print("error en API")
        data = response.json()
        try:
            if data:

                for d in range(len(data['REGISTRO'])):
                    dte = data['REGISTRO'][d]['dte']
                    receptor = CRut(data['REGISTRO'][d]['emisor'])
                    fecha = data['REGISTRO'][d]['fecha']
                    iva = data['REGISTRO'][d]['iva']
                    neto = data['REGISTRO'][d]['neto']
                    total = data['REGISTRO'][d]['total']
                    exento = data['REGISTRO'][d]['exento']
                    folio = data['REGISTRO'][d]['Folio']
                    razon_social = data['REGISTRO'][d]['razonSocial']
                    cod_entidad = rutCV

                    cursor.execute(
                        "select desc_conf_contribuyente from conf_contribuyente where rut_contribuyente=%s and rut_cliente_proveedor=%s and cod_tipo_configuracion=1",
                        [rutCV, receptor])
                    conf_contribuyente = cursor.fetchone()
                    fecha_modificada = datetime.strptime(fecha, '%d/%m/%Y')
                    cursor.execute(
                        "select rut_contribuyente,nombre_contribuyente from contribuyente where rut_contribuyente =%s",
                        [receptor])
                    ncontribuyente = cursor.fetchone()
                    try:
                        cursor.execute("select cod_registro_cv from registro_cv where cod_registro_cv=%s", [folio])
                        exist_folio = cursor.fetchone()
                    except:
                        db.rollback()
                        print("error no esperado", sys.exc_info())
                    if not exist_folio:
                        if not ncontribuyente:
                            try:
                                dias = 30
                                cursor.execute(
                                    "insert into contribuyente (rut_contribuyente,nombre_contribuyente) values(%s,%s)",
                                    [receptor, razon_social])
                                cursor.execute("""insert into conf_contribuyente (desc_conf_contribuyente,rut_contribuyente,rut_cliente_proveedor,cod_tipo_configuracion)values 
                                                                                       (%s,%s,%s,%s)""",
                                               [dias, rut_contribuyente, receptor, 1])
                                db.commit()
                            except:
                                db.rollback()
                                print("error no esperado", sys.exc_info())
                        if conf_contribuyente:
                            dias_cobro = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias_cobro)
                            cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                                            monto_iva,monto_total,saldo_documento)
                                                                                 values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                           [folio, dias_cobro, dte, cod_entidad, receptor, fecha_modificada,
                                            fecha_vencimiento,
                                            neto or 0,
                                            exento or 0, iva or 0,
                                            total or 0, total or 0])
                        else:
                            dias = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                            cursor.execute("""insert into registro_cv (cod_registro_cv,desc_registro_cv,cod_tipo_documento,receptor,emisor,fecha_emision,fecha_vencimiento,monto_neto,monto_excento,
                                        monto_iva,monto_total,saldo_documento)
                                                             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_cv""",
                                           [folio, dias, dte, cod_entidad, receptor, fecha_modificada,
                                            fecha_vencimiento,
                                            neto or 0,
                                            exento or 0, iva or 0,
                                            total or 0, total or 0])

                    else:
                        print("folio existe")
                        try:
                            dias = int(conf_contribuyente[0])
                            fecha_vencimiento = fecha_modificada + timedelta(days=dias)
                            cursor.execute("update registro_cv set fecha_vencimiento=%s where  cod_registro_cv=%s",
                                           [fecha_vencimiento, folio])
                        except:
                            db.rollback()
                            print("error no esperado", sys.exc_info())
                print("compras guardadas con exito")
                db.commit()
                success = 'actualizado'
                flash(success)
        except:
            db.rollback()
            print("error no esperado", sys.exc_info())

    return render_template('/egresos/compras.html', titulo=titulo, anio_actual=anio_actual, datosUsx=datosUsx,
                           contribuyentes=contribuyentes, dtsUser=dtsUser,
                           clientesUnicosComprasAnuales=clientesUnicosComprasAnuales,
                           clientesUnicosComprasMensuales=clientesUnicosComprasMensuales, mobs=mobs)


@mod_compra.route('/gastos/<rut_contribuyente>', methods=['GET', 'POST', 'UPDATE'])
def gastos(rut_contribuyente):
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
        contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        dtsUser = getContribuyente(cod_usuario[0])
        anio_actual = t
        titulo = 'Gastos'
        cursor.execute("select * from cuenta_gastos")
        cuenta_gastos = cursor.fetchall()
        if request.method == 'GET':
            try:
                cursor.execute("select * from gastos where rut_contribuyente=%s", [rut_contribuyente])
                gastos = cursor.fetchall()
                return render_template('/egresos/gastos.html', titulo=titulo, anio_actual=anio_actual,
                                       datosUsx=datosUsx, gastos=gastos,
                                       contribuyentes=contribuyentes, cuenta_gastos=cuenta_gastos, dtsUser=dtsUser)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor.execute(
                    """insert into gastos(desc_gastos,rut_contribuyente,monto,fecha,responsable,n_documento,nombre_contribuyente,
                    descripcion,archivo,periodo,negocio_asociado,cod_cuenta_gastos) values (%(desc_gastos)s,%(rut_contribuyente)s
                    ,%(monto)s,%(fecha)s,%(responsable)s,%(n_documento)s,%(nombre_contribuyente)s,
                    %(descripcion)s,%(archivo)s,%(periodo)s,%(negocio_asociado)s,%(cod_cuenta_gastos)s)""",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == "UPDATE":
            try:
                if request.content_type == 'application/json':
                    data = request.json

                cursor.execute(
                    """update  gastos set desc_gastos=%(desc_gastos)s,rut_contribuyente=%(rut_contribuyente)s,monto=%(monto)s,
                     fecha=%(fecha)s,responsable=%(responsable)s,n_documento=%(n_documento)s,nombre_contribuyente=%(nombre_contribuyente)s,
                     descripcion=%(descripcion)s,archivo=%(archivo)s,periodo=%(periodo)s,negocio_asociado=%(negocio_asociado)s,
                      cod_cuenta_gastos=%(cod_cuenta_gastos)s where cod_gastos=%(cod_gastos)s""",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/login')
