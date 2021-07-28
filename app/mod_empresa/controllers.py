import sys

import requests
from flask import Blueprint, session, render_template, request, flash, redirect
from app import db, app, t
from app.mod_auth.controllers import getContribuyente, getDatosUsuario, CRut

mod_empresa = Blueprint('empresa', __name__, url_prefix='/empresa')


@mod_empresa.route('/solicitudes/<estado>', methods=['GET', 'POST'])
def solicitudes(estado):
    if 'username' in session:
        cursor = db.cursor()
        cod_usuario = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where cod_usuario = %s", [cod_usuario[0]])
        contribuyentes = cursor.fetchall()
        respuesta = 'na'
        for c in range(len(contribuyentes)):
            cursor.execute(
                "select rut_contribuyente,rut_apoderado,clave_bancaria,cod_banco,cod_tipo_cuenta,cod_cuenta_bancaria from cuenta_bancaria where rut_contribuyente=%s",
                [contribuyentes[c][0]])
            cuentas = cursor.fetchone()
            if estado == 'procesando':
                try:
                    cursor.execute(
                        "insert into solicitudes (desc_solicitudes,estado,rut_contribuyente,cod_tipo_cuenta) values (%s,%s,%s,%s)",
                        ['saldos empresas', estado, cuentas[0], cuentas[4]])

                    respuesta = 'ok'
                except:
                    db.rollback()
                    print("error no esperado", sys.exc_info())
                    respuesta = 'error'
                    return respuesta
        db.commit()
        return respuesta


def saldosEmpresas(rut_contribuyente):
    cursor = db.cursor()
    cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
    contribuyentes = cursor.fetchall()
    dnis = []
    try:
        for c in range(len(contribuyentes)):
            cursor.execute(
                "select rut_contribuyente,rut_apoderado,clave_bancaria,cod_banco,cod_tipo_cuenta,cod_cuenta_bancaria from cuenta_bancaria where rut_contribuyente=%s",
                [contribuyentes[c][0]])
            cuentas = cursor.fetchone()
            dnis.append(cuentas)
            if cuentas[3] == 5:
                if cuentas[4] == 10:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/chile/empresa'
                    payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                        cuentas[1], cuentas[2])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = cuentas[5]
                            cursor.execute(
                                """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                                data2[0])
                        db.commit()
                        success = 'ok'
                        flash(success)
                    except:
                        db.rollback()
                        success = 'error'
                        flash(success)
                        print("error no esperado", sys.exc_info())
            elif cuentas[3] == 8:
                if cuentas[4] == 4:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/estado/empresa'
                    payload2 = '{"rut":"%s","rut_a":"%s","pass":"%s"}' % (
                        cuentas[0], cuentas[1], cuentas[2])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = cuentas[5]
                            cursor.execute(
                                """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                                data2[0])
                        db.commit()
                        success = 'ok'
                        flash(success)
                    except:
                        db.rollback()
                        success = 'error'
                        flash(success)
                        print("error no esperado", sys.exc_info())
            elif cuentas[3] == 4:
                if cuentas[4] == 3:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/santander/empresa'
                    payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                        cuentas[1], cuentas[2])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = cuentas[5]
                            cursor.execute(
                                """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                                data2[0])
                        db.commit()
                        success = 'ok'
                        flash(success)
                    except:
                        db.rollback()
                        success = 'error'
                        flash(success)
                        print("error no esperado", sys.exc_info())
            elif cuentas[3] == 7:
                if cuentas[4] == 8:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/bci/empresario'
                    payload2 = '{"rut":"%s","pass":"%s"}' % (
                        cuentas[1], cuentas[2])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = cuentas[5]
                            cursor.execute(
                                """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                                data2[0])
                        db.commit()
                        success = 'ok'
                        flash(success)
                    except:
                        db.rollback()
                        success = 'error'
                        flash(success)
                        print("error no esperado", sys.exc_info())
    except:
        success = 'error'
        flash(success)
        print("error no esperado", sys.exc_info())
        return success
    success = 'ok'
    return success



@mod_empresa.route('/seleccionarEmpresa', methods=['GET', 'POST','UPDATE'])
def seleccionarEmpresa():
    if 'username' in session:
        cursor = db.cursor()
        titulo = 'Flujappy'
        cod_usuario = getDatosUsuario(session['username'])
        anio_actual = t
        cursor.execute("select * from contribuyente where cod_usuario = %s", [cod_usuario[0]])
        contribuyentes = cursor.fetchall()
        dnis = []
        if request.method == "POST":
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor = db.cursor()
                cursor.execute("""insert into contribuyente(rut_contribuyente,nombre_contribuyente,clave_tributaria,cod_usuario,correo_contribuyente)
                 values (%(rut_contribuyente)s,%(nombre_contribuyente)s,%(clave_tributaria)s,%(cod_usuario)s,%(correo_contribuyente)s)""",
                               data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
        if request.method == "UPDATE":
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor = db.cursor()
                cursor.execute("update contribuyente set nombre_contribuyente=%(nombre_contribuyente)s,clave_tributaria=%(clave_tributaria)s,correo_contribuyente=%(correo_contribuyente)s  where rut_contribuyente=%(rut_contribuyente)s and cod_usuario=%(cod_usuario)s", data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
        if request.method == "GET":
            for c in range(len(contribuyentes)):
                cursor.execute("""select cuenta_bancaria.rut_contribuyente,rut_apoderado,clave_bancaria,cuenta_bancaria.cod_banco,cod_tipo_cuenta,saldo_cuenta,nombre_banco,nombre_contribuyente 
                from cuenta_bancaria,banco,contribuyente 
                where cuenta_bancaria.rut_contribuyente=%s and cuenta_bancaria.cod_banco = banco.cod_banco and cuenta_bancaria.rut_contribuyente = contribuyente.rut_contribuyente""",[contribuyentes[c][0]])
                cuentas = cursor.fetchone()
                dnis.append(cuentas)
            return render_template("/empresa/seleccionarEmpresa.html", contribuyentes=contribuyentes, titulo=titulo,
                               anio_actual=anio_actual, datosUsx=cod_usuario,dnis=dnis)
        # if 'btn_actualizar' in request.form:
        #     for c in range(len(contribuyentes)):
        #         cursor.execute("select rut_contribuyente,rut_apoderado,clave_bancaria,cod_banco,cod_tipo_cuenta,cod_cuenta_bancaria from cuenta_bancaria where rut_contribuyente=%s",[contribuyentes[c][0]])
        #         cuentas = cursor.fetchone()
        #         dnis.append(cuentas)
        #         if cuentas[3] == 8:
        #             if cuentas[4] == 4:
        #                 #######--------------------saldos-----------------------------------------------------------------
        #                 url_data2 = 'http://192.168.1.170:5001/saldo/estado/empresa'
        #                 payload2 = '{"rut":"%s","rut_a":"%s","pass":"%s"}' % (
        #                     cuentas[0], cuentas[1], cuentas[2])
        #
        #                 headers2 = {
        #                     'Content-Type': 'application/json'
        #                 }
        #                 response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
        #
        #                 if response2.status_code == 500:
        #                     print("error en API")
        #                 data2 = response2.json()
        #                 try:
        #                     if data2:
        #                         data2[0]['cod_cuenta_bancaria'] = cuentas[5]
        #                         cursor.execute(
        #                             """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
        #                             data2[0])
        #                     db.commit()
        #                     success = 'ok'
        #                     flash(success)
        #                 except:
        #                     db.rollback()
        #                     success = 'error'
        #                     flash(success)
        #                     print("error no esperado", sys.exc_info())
        #         elif cuentas[3] == 4:
        #             if cuentas[4] == 3:
        #                 #######--------------------saldos-----------------------------------------------------------------
        #                 url_data2 = 'http://192.168.1.170:5001/saldo/santander/empresa'
        #                 payload2 = '{"rut_a":"%s","pass":"%s"}' % (
        #                     cuentas[1], cuentas[2])
        #
        #                 headers2 = {
        #                     'Content-Type': 'application/json'
        #                 }
        #                 response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
        #
        #                 if response2.status_code == 500:
        #                     print("error en API")
        #                 data2 = response2.json()
        #                 try:
        #                     if data2:
        #                         data2[0]['cod_cuenta_bancaria'] = cuentas[5]
        #                         cursor.execute(
        #                             """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
        #                             data2[0])
        #                     db.commit()
        #                     success = 'ok'
        #                     flash(success)
        #                 except:
        #                     db.rollback()
        #                     success = 'error'
        #                     flash(success)
        #                     print("error no esperado", sys.exc_info())
        #         elif cuentas[3] == 7:
        #             if cuentas[4] == 8:
        #                 #######--------------------saldos-----------------------------------------------------------------
        #                 url_data2 = 'http://192.168.1.170:5001/saldo/bci/empresario'
        #                 payload2 = '{"rut":"%s","pass":"%s"}' % (
        #                     cuentas[1], cuentas[2])
        #
        #                 headers2 = {
        #                     'Content-Type': 'application/json'
        #                 }
        #                 response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
        #
        #                 if response2.status_code == 500:
        #                     print("error en API")
        #                 data2 = response2.json()
        #                 try:
        #                     if data2:
        #                         data2[0]['cod_cuenta_bancaria'] = cuentas[5]
        #                         cursor.execute(
        #                             """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
        #                             data2[0])
        #                     db.commit()
        #                     success = 'ok'
        #                     flash(success)
        #                 except:
        #                     db.rollback()
        #                     success = 'error'
        #                     flash(success)
        #                     print("error no esperado", sys.exc_info())
        return render_template("/empresa/seleccionarEmpresa.html", contribuyentes=contribuyentes, titulo=titulo,
                               anio_actual=anio_actual, datosUsx=cod_usuario, dnis=dnis)
    return redirect('/auth/login')


@mod_empresa.route('/dashboardEmpresa/<rut_contribuyente>', methods=['GET', 'POST'])
def dashboardEmpresa(rut_contribuyente):

    if 'username' in session:
        cursor = db.cursor()
        cursor.execute("select * from indicadores")
        indicadores = cursor.fetchall()
        cursor.execute(
            "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s  ",
            [rut_contribuyente])
        clientesUnicosComprasAnuales = cursor.fetchone()
        cursor.execute(
            "select count(DISTINCT emisor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and receptor = %s and EXTRACT(MONTH FROM fecha_emision) = extract(month from now()) ",
            [rut_contribuyente])
        clientesUnicosComprasMensuales = cursor.fetchone()

        cursor.execute(
            "select count(DISTINCT receptor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and emisor = %s  ",
            [rut_contribuyente])
        clientesUnicosVentasAnuales = cursor.fetchone()
        cursor.execute(
            "select count(DISTINCT receptor) from registro_cv where extract(year from now())=EXTRACT(year FROM fecha_emision) and emisor = %s and EXTRACT(MONTH FROM fecha_emision) = extract(month from now()) ",
            [rut_contribuyente])
        clientesUnicosVentasMensuales = cursor.fetchone()

        titulo = 'Dashboard Empresa'
        cod_usuario = getDatosUsuario(session['username'])
        anio_actual = t
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
        contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        dtsUser = getContribuyente(cod_usuario[0])
        cursor.execute("select * from registro_cv where emisor=%s", [rut_contribuyente])
        vtas = cursor.fetchall()
        graficoCantidades = []
        graficoCount = []
        cursor.execute("select * from registro_cv where receptor=%s ", [rut_contribuyente])
        cprs = cursor.fetchall()
        graficoCantidadesCompra = []
        graficoCountCompra = []
        # --------------------------------VENTAS----------------------------------------------------------------------
        cursor.execute("select count(desc_registro_cv) from registro_cv where emisor = %s", [rut_contribuyente])
        cantidadTotalAnual = cursor.fetchone()
        cursor.execute("select sum(monto_total) from registro_cv where emisor = %s", [rut_contribuyente])
        totalVentas = cursor.fetchone()
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,count(desc_registro_cv) from registro_cv where emisor = %s and 
                                    extract(year from now())=EXTRACT(year FROM fecha_emision)
                                    GROUP BY mes,anio order by mes asc""", [rut_contribuyente])
        ventasCount = cursor.fetchall()
        for v in range(len(list(ventasCount))):
            objGraficoCount = {
                'anio': int(ventasCount[v][1]),
                'mes': int(ventasCount[v][0]),
                'cantidad': int(ventasCount[v][-1])
            }

            graficoCount.append(objGraficoCount)
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,sum(monto_total) from registro_cv where emisor = %s and 
                                    extract(year from now())=EXTRACT(year FROM fecha_emision)
                                    GROUP BY mes,anio order by mes asc""", [rut_contribuyente])
        ventasGrafico = cursor.fetchall()
        for v in range(len(list(ventasGrafico))):
            objGraficoCantidades = {
                'anio': int(ventasGrafico[v][1]),
                'mes': int(ventasGrafico[v][0]),
                'cantidad': int(ventasGrafico[v][-1])
            }

            graficoCantidades.append(objGraficoCantidades)

        # -------------------------------COMPRAS-----------------------------------------------------------------------
        cursor.execute("select count(desc_registro_cv) from registro_cv where receptor = %s", [rut_contribuyente])
        cantidadTotalAnualCompras = cursor.fetchone()
        cursor.execute("select sum(monto_total) from registro_cv where receptor = %s", [rut_contribuyente])
        totalCompras = cursor.fetchone()
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,count(desc_registro_cv) from registro_cv where receptor = %s and 
                                            extract(year from now())=EXTRACT(year FROM fecha_emision)
                                            GROUP BY mes,anio order by mes asc""", [rut_contribuyente])
        comprasCount = cursor.fetchall()
        for v in range(len(list(comprasCount))):
            objGraficoCount = {
                'anio': int(comprasCount[v][1]),
                'mes': int(comprasCount[v][0]),
                'cantidad': int(comprasCount[v][-1])
            }

            graficoCountCompra.append(objGraficoCount)
        cursor.execute("""select EXTRACT(MONTH FROM fecha_emision) as mes,EXTRACT(year FROM fecha_emision) as anio,sum(monto_total) from registro_cv where receptor = %s and 
                                            extract(year from now())=EXTRACT(year FROM fecha_emision)
                                            GROUP BY mes,anio order by mes asc""", [rut_contribuyente])
        comprasGrafico = cursor.fetchall()
        for v in range(len(list(comprasGrafico))):
            objGraficoCantidades = {
                'anio': int(comprasGrafico[v][1]),
                'mes': int(comprasGrafico[v][0]),
                'cantidad': int(comprasGrafico[v][-1])
            }

            graficoCantidadesCompra.append(objGraficoCantidades)
        cursor.execute("""select desc_cuenta_gastos,sum(monto) as total from gastos,cuenta_gastos where rut_contribuyente = %s and cuenta_gastos.cod_cuenta_gastos = gastos.cod_cuenta_gastos GROUP BY
                            desc_cuenta_gastos""",[rut_contribuyente])
        gastos = cursor.fetchall()
        cursor.execute("select saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s",[rut_contribuyente])
        saldoCuenta = cursor.fetchone()
        cursor.execute("select cod_cuenta_bancaria from cuenta_bancaria where rut_contribuyente=%s",[rut_contribuyente])
        cod_cuenta_bancaria = cursor.fetchone()
        if cod_cuenta_bancaria:
            cursor.execute("select sum(abono)abono,sum(cargo)cargo from movimiento_cb where cod_cuenta_bancaria=%s",[cod_cuenta_bancaria[0]])
            abonoCargo = cursor.fetchone()
            cursor.execute("""select EXTRACT(MONTH FROM fecha_movimiento) as mes,EXTRACT(year FROM fecha_movimiento) as anio,sum(abono) from movimiento_cb where cod_cuenta_bancaria=%s and 
                                                extract(year from now())=EXTRACT(year FROM fecha_movimiento)
                                                GROUP BY mes,anio order by mes asc""",[cod_cuenta_bancaria[0]])
            abonoMensual = cursor.fetchall()
            cursor.execute("""select EXTRACT(MONTH FROM fecha_movimiento) as mes,EXTRACT(year FROM fecha_movimiento) as anio,sum(cargo) from movimiento_cb where cod_cuenta_bancaria=%s and 
                                                        extract(year from now())=EXTRACT(year FROM fecha_movimiento)
                                                        GROUP BY mes,anio order by mes asc""", [cod_cuenta_bancaria[0]])
            cargoMensual = cursor.fetchall()
        else:
            abonoCargo='na'
            abonoMensual='na'
            cargoMensual='na'
        if request.method == "POST":
            url_data = 'http://192.168.1.91:5001/indicadores'
            payload = '{"mes":"%s","anio":"%s"}' % (
                'a','a')

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url_data, headers=headers, data=payload)
            if response.status_code == 500:
                print("error en API")
            dataIndicadores = response.json()
            if indicadores:
                for d in range(1, len(dataIndicadores)):
                    try:
                        cursor.execute(
                            "update indicadores set valor=%s where desc_indicadores=%s",[list(dataIndicadores.keys())[d],
                            list(dataIndicadores.values())[d]])
                    except:
                        db.rollback()
                        print("error no esperado", sys.exc_info())
                db.commit()
            else:
                for d in range(1, len(dataIndicadores)):
                    try:
                        cursor.execute("insert into indicadores (desc_indicadores,valor)values(%s,%s)",[list(dataIndicadores.keys())[d],list(dataIndicadores.values())[d]])
                    except:
                        db.rollback()
                        mensaje = 'error'
                        flash(mensaje)
                        print("error no esperado", sys.exc_info())
                mensaje='actualizado'
                flash(mensaje)
                db.commit()
        return render_template("/empresa/dashboardEmpresa.html", contribuyentes=contribuyentes, titulo=titulo,
                               anio_actual=anio_actual, cod_usuario=cod_usuario, vtas=vtas,cprs=cprs,
                               graficoCantidades=graficoCantidades, graficoCount=graficoCount,
                               totalVentas=totalVentas, cantidadTotalAnual=cantidadTotalAnual,
                               cantidadTotalAnualCompras=cantidadTotalAnualCompras,
                               totalCompras=totalCompras, graficoCantidadesCompra=graficoCantidadesCompra,clientesUnicosVentasMensuales=clientesUnicosVentasMensuales,
                               clientesUnicosComprasAnuales=clientesUnicosComprasAnuales,clientesUnicosVentasAnuales=clientesUnicosVentasAnuales,
                               clientesUnicosComprasMensuales=clientesUnicosComprasMensuales,abonoCargo=abonoCargo,abonoMensual=abonoMensual,cargoMensual=cargoMensual,
                               graficoCountCompra=graficoCountCompra,gastos=gastos,dtsUser=dtsUser,datosUsx=datosUsx,saldoCuenta=saldoCuenta,indicadores=indicadores)
    return redirect('/auth/login')
