from decimal import Decimal
import json
import sys
import simplejson as json
import requests

from app.mod_auth.controllers import getDatosUsuario, getContribuyente, getCuentaContribuyente, dictfetchall, \
    myconverter
from flask import Blueprint, session, render_template, request, redirect, flash, jsonify
from app import db, app, t


mod_bancos = Blueprint('bancos', __name__, url_prefix='/bancos')


@mod_bancos.route('/solicitudes/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>/<estado>/<cod_banco>/<inicio>/<fin>',methods=['GET', 'POST'])
def solicitudes(rut_contribuyente,tipo_cuenta,mes,anio,estado,cod_banco,inicio,fin):
    cursor = db.cursor()
    desc_cartola = mes + '-' + anio
    tipo_cuenta = int(tipo_cuenta)
    if estado == 'procesando':
        try:
            cursor.execute("insert into solicitudes (desc_solicitudes,estado,rut_contribuyente,cod_tipo_cuenta,desc_cartola,anio,mes,cod_bancos,inicio,fin) values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)",['solicitud',estado,rut_contribuyente,tipo_cuenta,desc_cartola,anio,mes,cod_banco,inicio,fin])
            db.commit()
            respuesta = 'ok'
            return respuesta
        except:
            db.rollback()
            print("error no esperado", sys.exc_info())
            respuesta = 'error'
            return respuesta


@mod_bancos.route('/conciliacion/<desc_conciliacion>/<cod_movimiento_cb>/<cod_registro_cv>/<monto_sii>/<monto_banco>',methods=['GET', 'POST'])
def conciliacion(desc_conciliacion, cod_movimiento_cb, cod_registro_cv, monto_sii, monto_banco):
    cursor = db.cursor()
    monto_banco = int(monto_banco.replace(",",""))
    monto_sii = int(monto_sii.replace(",",""))
    conciliacion = monto_sii - monto_banco
    try:
        cursor.execute(
            """insert into conciliacion (desc_conciliacion,cod_movimiento_cb,cod_registro_cv,monto_conciliacion)values (%s,%s,%s,%s)"""
            , [desc_conciliacion, cod_movimiento_cb, cod_registro_cv, conciliacion])
        cursor.execute("update registro_cv set estado_documento='conciliada' where cod_registro_cv=%s",[cod_registro_cv])
        cursor.execute("update movimiento_cb set estado_bancaria='conciliada' where cod_movimiento_cb=%s",[cod_movimiento_cb])
        db.commit()
        return print("ok")
    except:
        db.rollback()
        print("error no esperado", sys.exc_info())
        return print("error")


@mod_bancos.route('/bancosAsociados/<rut_contribuyente>', methods=['GET','POST'])
def bancosAsociados(rut_contribuyente):
    cursor = db.cursor()
    cursor.execute(
        "select cuenta_bancaria.cod_banco,nombre_banco,estado_banco from cuenta_bancaria,banco where rut_contribuyente=%s and banco.cod_banco= cuenta_bancaria.cod_banco",
        [rut_contribuyente])
    bancos_asociados = cursor.fetchall()
    cuentaBancaria = getCuentaContribuyente(rut_contribuyente)
    bancos_a = []
    for c in range(len(list(bancos_asociados))):
        objData = {
            'cod_banco': bancos_asociados[c][0],
            'nombre_banco': bancos_asociados[c][1],
            'cuenta_bancaria': cuentaBancaria[0][0],
            'rut_apoderado': cuentaBancaria[0][2],
            'estado_banco': bancos_asociados[c][2]
        }
        bancos_a.append(objData)
    response = app.response_class(
        response=json.dumps(bancos_a),
        status=200,
        mimetype='application/json'
    )
    return response


class DecimalEncoder (json.JSONEncoder):
    def default (self, obj):
       if isinstance (obj, Decimal):
           return int (obj)
       return json.JSONEncoder.default (self, obj)


@mod_bancos.route('/abonoCargo/<mes>/<anio>', methods=["GET", "POST", "UPDATE"])
def abonoCargo(mes,anio):
    cursor = db.cursor()
    desc_cartola = mes+'-'+anio
    cursor.execute("select cod_cartola_bancaria from cartola_bancaria where desc_cartola_bancaria=%s",[desc_cartola])
    cod_cartola = cursor.fetchone()
    cursor.execute("select desc_movimiento_cb,cod_cuenta_bancaria,num_documento,round(cargo)cargo,round(abono)abono,fecha_movimiento,cod_cartola_bancaria,estado_bancaria from movimiento_cb where cod_cartola_bancaria =%s",[cod_cartola])
    movimientos = cursor.fetchall()
    a =json.dumps(movimientos, use_decimal=True,default=myconverter)
    return a


def actualizarBanco(rut_contribuyente,tipo_cuenta,mes,anio,cod_banco,inicio,fin):
    if cod_banco == 5:
        tipo_cuenta = int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes + '-' + anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s",
                       [rut_contribuyente, tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute(
            """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=8 and cod_tipo_cuenta=%s""",
            [rut_contribuyente, rut_contribuyente, tipo_cuenta])
        ctaBancariaEstadoEmpresa = cursor.fetchone()
        if tipo_cuenta == 10:
            cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                           [ctaBancariaEstadoEmpresa[0]])
            movimiento_cb = cursor.fetchall()
            cursor.execute(
                "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                [ctaBancariaEstadoEmpresa[0], desc_cartola])
            cartolaBancaria = cursor.fetchone()
            url_data = 'http://192.168.1.170:5001/cartola/chile/empresa'
            payload = '{"rut_a":"%s","pass":"%s","inicio":"%s","fin":"%s"}' % (
                ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4], inicio, fin)

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url_data, headers=headers, data=payload)
            if response.status_code == 500:
                print("error en API")
            data = response.json()
            #######--------------------saldos-----------------------------------------------------------------
            url_data2 = 'http://192.168.1.170:5001/saldo/chile/empresa'
            payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4])

            headers2 = {
                'Content-Type': 'application/json'
            }
            response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

            if response2.status_code == 500:
                print("error en API")
            data2 = response2.json()
            try:
                if data:
                    if cartolaBancaria:
                        cursor.execute(
                            "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                            [cartolaBancaria[0]])
                        print("cartola existe")
                        db.commit()
                        estado = False
                        for d in range(0, len(data)):
                            data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                            data[d]['estado_bancaria'] = 'no conciliada'
                            print(d)
                            estado = False

                            for m in range(0, (len(movimiento_cb))):
                                if data[d]['n_documento'] in movimiento_cb[m][6]:
                                    estado = True
                                    print("exist not modified")
                            if estado == False:
                                cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                                cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                                values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                               data[d])
                                cod_movimiento_cb = cursor.fetchone()[0]
                                cursor.execute(
                                    """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                    [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                                print(data[d])
                                success = 'actualizado'
                                flash(success)
                        db.commit()
                    else:
                        cursor.execute(
                            """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                            [desc_cartola, ctaBancariaEstadoEmpresa[0]])
                        cod_cartola_bancaria = cursor.fetchone()[0]

                        for d in range(1, len(data)):
                            data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                            data[d]['estado_bancaria'] = 'no conciliada'
                            cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                            cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                            values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                           data[d])
                            cod_movimiento_cb = cursor.fetchone()[0]

                            cursor.execute(
                                """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                            print(data[d])
                        db.commit()
                        success = 'actualizado'
                        flash(success)
            except:
                db.rollback()
                print("error no esperado", sys.exc_info())
            try:
                if data2:
                    data2[0]['cod_cuenta_bancaria'] = ctaBancariaEstadoEmpresa[0]
                    cursor.execute(
                        """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                        data2[0])
                db.commit()
            except:
                db.rollback()
                error = 'error'
                flash(error)
                print("error no esperado", sys.exc_info())
                return error
        success = 'ok'
        flash(success)
        return success
    if cod_banco == 8:
        tipo_cuenta = int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes + '-' + anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s",
                       [rut_contribuyente, tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute(
            """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=8 and cod_tipo_cuenta=%s""",
            [rut_contribuyente, rut_contribuyente, tipo_cuenta])
        ctaBancariaEstadoEmpresa = cursor.fetchone()
        if tipo_cuenta == 4:
            cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                           [ctaBancariaEstadoEmpresa[0]])
            movimiento_cb = cursor.fetchall()
            cursor.execute(
                "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                [ctaBancariaEstadoEmpresa[0], desc_cartola])
            cartolaBancaria = cursor.fetchone()
            url_data = 'http://192.168.1.170:5001/cartola/estado/empresa'
            payload = '{"rut":"%s","rut_a":"%s","pass":"%s","inicio":"%s","fin":"%s"}' % (
                ctaBancariaEstadoEmpresa[1], ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4], inicio, fin)

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url_data, headers=headers, data=payload)
            if response.status_code == 500:
                print("error en API")
            data = response.json()
            #######--------------------saldos-----------------------------------------------------------------
            url_data2 = 'http://192.168.1.170:5001/saldo/estado/empresa'
            payload2 = '{"rut":"%s","rut_a":"%s","pass":"%s"}' % (
                ctaBancariaEstadoEmpresa[1], ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4])

            headers2 = {
                'Content-Type': 'application/json'
            }
            response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

            if response2.status_code == 500:
                print("error en API")
            data2 = response2.json()
            try:
                if data:
                    if cartolaBancaria:
                        cursor.execute(
                            "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                            [cartolaBancaria[0]])
                        print("cartola existe")
                        db.commit()
                        estado = False
                        for d in range(0, len(data)):
                            data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                            data[d]['estado_bancaria'] = 'no conciliada'
                            print(d)
                            estado = False

                            for m in range(0, (len(movimiento_cb))):
                                if data[d]['n_documento'] in movimiento_cb[m][6]:
                                    estado = True
                                    print("exist not modified")
                            if estado == False:
                                cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                             cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                             values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                               data[d])
                                cod_movimiento_cb = cursor.fetchone()[0]
                                cursor.execute(
                                    """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                    [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                                print(data[d])
                                success = 'actualizado'
                                flash(success)
                        db.commit()
                    else:
                        cursor.execute(
                            """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                            [desc_cartola, ctaBancariaEstadoEmpresa[0]])
                        cod_cartola_bancaria = cursor.fetchone()[0]

                        for d in range(1, len(data)):
                            data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                            data[d]['estado_bancaria'] = 'no conciliada'
                            cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                         cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                         values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                           data[d])
                            cod_movimiento_cb = cursor.fetchone()[0]

                            cursor.execute(
                                """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                            print(data[d])
                        db.commit()
                        success = 'actualizado'
                        flash(success)
            except:
                db.rollback()
                print("error no esperado", sys.exc_info())
            try:
                if data2:
                    data2[0]['cod_cuenta_bancaria'] = ctaBancariaEstadoEmpresa[0]
                    cursor.execute(
                        """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                        data2[0])
                db.commit()
            except:
                db.rollback()
                error = 'error'
                flash(error)
                print("error no esperado", sys.exc_info())
                return error
        success = 'ok'
        flash(success)
        return success
    elif cod_banco == 4:
        tipo_cuenta = int(tipo_cuenta)
        cursor = db.cursor()
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s",
                       [rut_contribuyente, tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute(
            """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=4 and cod_tipo_cuenta=%s""",
            [rut_contribuyente, rut_contribuyente, tipo_cuenta])
        ctaBancariaSantanderEmpresa = cursor.fetchone()
        cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                       [ctaBancariaSantanderEmpresa[0]])
        movimiento_cb = cursor.fetchall()
        if tipo_cuenta == 3:
            desc_cartola = mes + '-' + anio
            cursor.execute(
                "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                [ctaBancariaSantanderEmpresa[0], desc_cartola])
            cartolaBancaria = cursor.fetchone()
            url_data = 'http://192.168.1.91:5001/cartola/santander/empresa'
            payload = '{"rut_a":"%s","pass":"%s","mes":"%s","anio":"%s"}' % (
                ctaBancariaSantanderEmpresa[3], ctaBancariaSantanderEmpresa[4], mes, anio)

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url_data, headers=headers, data=payload)
            if response.status_code == 500:
                print("error en API")
            data = response.json()
            #######--------------------saldos-----------------------------------------------------------------
            url_data2 = 'http://192.168.1.91:5001/saldo/santander/empresa'
            payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                ctaBancariaSantanderEmpresa[3], ctaBancariaSantanderEmpresa[4])

            headers2 = {
                'Content-Type': 'application/json'
            }
            response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

            if response2.status_code == 500:
                print("error en API")
            data2 = response2.json()
            try:
                if data:
                    if cartolaBancaria:
                        cursor.execute(
                            "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                            [cartolaBancaria[0]])
                        print("cartola existe")
                        db.commit()
                        estado = False
                        for d in range(0, len(data)):
                            data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                            data[d]['estado_bancaria'] = 'no conciliada'
                            print(d)
                            estado = False

                            for m in range(0, (len(movimiento_cb))):
                                if data[d]['n_documento'] in movimiento_cb[m][6]:
                                    estado = True
                                    print("exist not modified")
                            if estado == False:
                                cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                             cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                             values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                               data[d])
                                cod_movimiento_cb = cursor.fetchone()[0]
                                cursor.execute(
                                    """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                    [ctaBancariaSantanderEmpresa[0], cod_movimiento_cb])
                                print(data[d])
                                success = 'actualizado'
                                flash(success)
                        db.commit()
                    else:
                        cursor.execute(
                            """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                            [desc_cartola, ctaBancariaSantanderEmpresa[0]])
                        cod_cartola_bancaria = cursor.fetchone()[0]

                        for d in range(1, len(data)):
                            data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                            data[d]['estado_bancaria'] = 'no conciliada'
                            cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                         cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                         values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                           data[d])
                            cod_movimiento_cb = cursor.fetchone()[0]

                            cursor.execute(
                                """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                [ctaBancariaSantanderEmpresa[0], cod_movimiento_cb])
                            print(data[d])
                        db.commit()
                        success = 'actualizado'
                        flash(success)
            except:
                db.rollback()
                print("error no esperado", sys.exc_info())
            try:
                if data2:
                    data2[0]['cod_cuenta_bancaria'] = ctaBancariaSantanderEmpresa[0]
                    cursor.execute(
                        """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                        data2[0])
                db.commit()
            except:
                db.rollback()
                error = 'error'
                flash(error)
                print("error no esperado", sys.exc_info())
                return error
        ok = 'ok'
        flash(ok)
        return ok
    elif cod_banco == 7:
        desc_cartola = mes + '-' + anio
        tipo_cuenta = int(tipo_cuenta)
        cursor = db.cursor()
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s",
                       [rut_contribuyente, tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute(
            """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=7 and cod_tipo_cuenta=%s""",
            [rut_contribuyente, rut_contribuyente, tipo_cuenta])
        ctaBancariaBciEmpresa = cursor.fetchone()
        cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                       [ctaBancariaBciEmpresa[0]])
        movimiento_cb = cursor.fetchall()
        if tipo_cuenta == 8:
            cursor.execute(
                "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                [ctaBancariaBciEmpresa[0], desc_cartola])
            cartolaBancaria = cursor.fetchone()
            url_data = 'http://192.168.0.14:5001/cartola/bci/empresario'
            payload = '{"rut":"%s","pass":"%s","mes":"%s","anio":"%s"}' % (
                ctaBancariaBciEmpresa[3], ctaBancariaBciEmpresa[4], mes, anio)

            headers = {
                'Content-Type': 'application/json'
            }
            response = requests.request("GET", url_data, headers=headers, data=payload)
            if response.status_code == 500:
                print("error en API")
            data = response.json()
            #######--------------------saldos-----------------------------------------------------------------
            url_data2 = 'http://192.168.0.14:5001/saldo/bci/empresario'
            payload2 = '{"rut":"%s","pass":"%s"}' % (
                ctaBancariaBciEmpresa[3], ctaBancariaBciEmpresa[4])

            headers2 = {
                'Content-Type': 'application/json'
            }
            response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

            if response2.status_code == 500:
                print("error en API")
            data2 = response2.json()
            try:
                if data:
                    if cartolaBancaria:
                        cursor.execute(
                            "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                            [cartolaBancaria[0]])
                        print("cartola existe")
                        db.commit()
                        estado = False
                        for d in range(0, len(data)):
                            data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                            data[d]['estado_bancaria'] = 'no conciliada'
                            print(d)
                            estado = False

                            for m in range(0, (len(movimiento_cb))):
                                if data[d]['n_documento'] in movimiento_cb[m][6]:
                                    estado = True
                                    print("exist not modified")
                            if estado == False:
                                cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                             cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                             values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                               data[d])
                                cod_movimiento_cb = cursor.fetchone()[0]
                                cursor.execute(
                                    """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                    [ctaBancariaBciEmpresa[0], cod_movimiento_cb])
                                print(data[d])
                                success = 'actualizado'
                                flash(success)
                        db.commit()
                    else:
                        cursor.execute(
                            """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                            [desc_cartola, ctaBancariaBciEmpresa[0]])
                        cod_cartola_bancaria = cursor.fetchone()[0]

                        for d in range(1, len(data)):
                            data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                            data[d]['estado_bancaria'] = 'no conciliada'
                            cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                                         cargo,abono,cod_cartola_bancaria,estado_bancaria)
                                         values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                                           data[d])
                            cod_movimiento_cb = cursor.fetchone()[0]

                            cursor.execute(
                                """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                                [ctaBancariaBciEmpresa[0], cod_movimiento_cb])
                            print(data[d])
                        db.commit()
                        success = 'actualizado'
                        flash(success)
            except:
                db.rollback()
                print("error no esperado", sys.exc_info())
            try:
                if data2:
                    data2[0]['cod_cuenta_bancaria'] = ctaBancariaBciEmpresa[0]
                    cursor.execute(
                        """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                        data2[0])
                db.commit()
            except:
                db.rollback()
                error = 'error'
                flash(error)
                print("error no esperado", sys.exc_info())
                return error
        ok = 'ok'
        flash(ok)
        return ok


@mod_bancos.route('/bancoChile/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>', methods=["GET", "POST", "UPDATE"])
def bancoChile(rut_contribuyente,tipo_cuenta,mes,anio):
    if 'username' in session:
        tipo_cuenta =int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes+'-'+anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s", [rut_contribuyente,tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                from registro_cv, contribuyente
                where (receptor=%s) and rut_contribuyente=emisor""", [contribuyentes[0][0]])
        compra_cv = cursor.fetchall()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                        from registro_cv, contribuyente
                        where (emisor=%s) and rut_contribuyente=receptor""", [contribuyentes[0][0]])
        venta_cv = cursor.fetchall()
        dtsUser = getContribuyente(cod_usuario[0])
        try:
            cursor.execute("""select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=8 and cod_tipo_cuenta=%s""",[rut_contribuyente,rut_contribuyente,tipo_cuenta])
            ctaBancariaChileEmpresa = cursor.fetchone()
            if ctaBancariaChileEmpresa:
                ###conciliacion compra
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                              from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                              where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                              and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.emisor
                                              and receptor = %s
                                              group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente
                                              """, [ctaBancariaChileEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasCompras = cursor.fetchall()
                ### conciliacion ventas
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                                              from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                                              where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                                              and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.receptor
                                                              and emisor = %s
                                                              group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente""",
                               [ctaBancariaChileEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasVentas = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                               [ctaBancariaChileEmpresa[0],desc_cartola])
                cartolaBancaria = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s",[ctaBancariaChileEmpresa[0]])
                cartolaHistorica = cursor.fetchall()
                cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                               [ctaBancariaChileEmpresa[0]])
                movimiento_cb = cursor.fetchall()
                if request.method == "GET":
                    return render_template("/bancos/bancoChile.html", contribuyentes=contribuyentes,
                                           anio_actual=anio_actual, datosUsx=datosUsx, dtsUser=dtsUser,
                                           movimiento_cb=movimiento_cb,
                                           ctaBancariaChileEmpresa=ctaBancariaChileEmpresa,
                                           cartolaBancaria=cartolaBancaria,cartolaHistorica=cartolaHistorica,compra_cv=compra_cv,venta_cv=venta_cv,conciliacionesBancariasCompras=conciliacionesBancariasCompras,
                                           conciliacionesBancariasVentas=conciliacionesBancariasVentas)
                if 'saldos' in request.form:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/chile/empresa'
                    payload2 = '{"rut":"%s","pass":"%s"}' % (
                        ctaBancariaChileEmpresa[1], ctaBancariaChileEmpresa[4])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = ctaBancariaChileEmpresa[0]
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
            return redirect('/auth/login')


@mod_bancos.route('/bancoEstado/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>', methods=["GET", "POST", "UPDATE"])
def bancoEstado(rut_contribuyente,tipo_cuenta,mes,anio):
    if 'username' in session:
        tipo_cuenta =int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes+'-'+anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s", [rut_contribuyente,tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                from registro_cv, contribuyente
                where (receptor=%s) and rut_contribuyente=emisor""", [contribuyentes[0][0]])
        compra_cv = cursor.fetchall()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                        from registro_cv, contribuyente
                        where (emisor=%s) and rut_contribuyente=receptor""", [contribuyentes[0][0]])
        venta_cv = cursor.fetchall()
        dtsUser = getContribuyente(cod_usuario[0])
        try:
            cursor.execute("""select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=8 and cod_tipo_cuenta=%s""",[rut_contribuyente,rut_contribuyente,tipo_cuenta])
            ctaBancariaEstadoEmpresa = cursor.fetchone()
            if ctaBancariaEstadoEmpresa:
                ###conciliacion compra
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                              from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                              where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                              and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.emisor
                                              and receptor = %s
                                              group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente
                                              """, [ctaBancariaEstadoEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasCompras = cursor.fetchall()
                ### conciliacion ventas
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                                              from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                                              where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                                              and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.receptor
                                                              and emisor = %s
                                                              group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente""",
                               [ctaBancariaEstadoEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasVentas = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                               [ctaBancariaEstadoEmpresa[0],desc_cartola])
                cartolaBancaria = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s",[ctaBancariaEstadoEmpresa[0]])
                cartolaHistorica = cursor.fetchall()
                cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                               [ctaBancariaEstadoEmpresa[0]])
                movimiento_cb = cursor.fetchall()
                if request.method == "GET":
                    return render_template("/bancos/bancoEstado.html", contribuyentes=contribuyentes,
                                           anio_actual=anio_actual, datosUsx=datosUsx, dtsUser=dtsUser,
                                           movimiento_cb=movimiento_cb,
                                           ctaBancariaEstadoEmpresa=ctaBancariaEstadoEmpresa,
                                           cartolaBancaria=cartolaBancaria,cartolaHistorica=cartolaHistorica,compra_cv=compra_cv,venta_cv=venta_cv,conciliacionesBancariasCompras=conciliacionesBancariasCompras,
                                           conciliacionesBancariasVentas=conciliacionesBancariasVentas)
                if 'saldos' in request.form:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.1.170:5001/saldo/estado/empresa'
                    payload2 = '{"rut":"%s","rut_a":"%s","pass":"%s"}' % (
                        ctaBancariaEstadoEmpresa[1], ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = ctaBancariaEstadoEmpresa[0]
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
                # if request.method == "POST":
                #     if tipo_cuenta == 4:
                #         anio = request.form["anio"]
                #         mes = request.form["mes"]
                #         inicio = request.form["inicio"]
                #         fin = request.form["fin"]
                #         desc_cartola = mes +'-'+anio
                #         cursor.execute(
                #             "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                #             [ctaBancariaEstadoEmpresa[0], desc_cartola])
                #         cartolaBancaria = cursor.fetchone()
                #         url_data = 'http://192.168.1.170:5001/cartola/estado/empresa'
                #         payload = '{"rut":"%s","rut_a":"%s","pass":"%s","inicio":"%s","fin":"%s"}' % (
                #             ctaBancariaEstadoEmpresa[1],ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4],inicio,fin)
                #
                #         headers = {
                #             'Content-Type': 'application/json'
                #         }
                #         response = requests.request("GET", url_data, headers=headers, data=payload)
                #         if response.status_code == 500:
                #             print("error en API")
                #         data = response.json()
                #         #######--------------------saldos-----------------------------------------------------------------
                #         url_data2 = 'http://192.168.1.170:5001/saldo/estado/empresa'
                #         payload2 = '{"rut":"%s","rut_a":"%s","pass":"%s"}' % (
                #             ctaBancariaEstadoEmpresa[1],ctaBancariaEstadoEmpresa[3], ctaBancariaEstadoEmpresa[4])
                #
                #         headers2 = {
                #             'Content-Type': 'application/json'
                #         }
                #         response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
                #
                #         if response2.status_code == 500:
                #             print("error en API")
                #         data2 = response2.json()
                #         try:
                #             if data:
                #                 if cartolaBancaria:
                #                     cursor.execute(
                #                         "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                #                         [cartolaBancaria[0]])
                #                     print("cartola existe")
                #                     db.commit()
                #                     estado = False
                #                     for d in range(0, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         print(d)
                #                         estado = False
                #
                #                         for m in range(0, (len(movimiento_cb))):
                #                             if data[d]['n_documento'] in movimiento_cb[m][6]:
                #                                 estado = True
                #                                 print("exist not modified")
                #                         if estado == False:
                #                             cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                          cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                          values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                            data[d])
                #                             cod_movimiento_cb = cursor.fetchone()[0]
                #                             cursor.execute(
                #                                 """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                                 [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                #                             print(data[d])
                #                             success = 'actualizado'
                #                             flash(success)
                #                     db.commit()
                #                 else:
                #                     cursor.execute(
                #                         """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                #                         [desc_cartola, ctaBancariaEstadoEmpresa[0]])
                #                     cod_cartola_bancaria = cursor.fetchone()[0]
                #
                #                     for d in range(1, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                      cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                      values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                        data[d])
                #                         cod_movimiento_cb = cursor.fetchone()[0]
                #
                #                         cursor.execute(
                #                             """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                             [ctaBancariaEstadoEmpresa[0], cod_movimiento_cb])
                #                         print(data[d])
                #                     db.commit()
                #                     success = 'actualizado'
                #                     flash(success)
                #         except:
                #             db.rollback()
                #             print("error no esperado", sys.exc_info())
                #         try:
                #             if data2:
                #                 data2[0]['cod_cuenta_bancaria'] = ctaBancariaEstadoEmpresa[0]
                #                 cursor.execute(
                #                     """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                #                     data2[0])
                #             db.commit()
                #         except:
                #             db.rollback()
                #             success = 'error'
                #             flash(success)
                #             print("error no esperado", sys.exc_info())
        except:
            return redirect('/auth/login')


@mod_bancos.route('/bancoSantander/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>', methods=["GET", "POST", "UPDATE"])
def bancoSantander(rut_contribuyente,tipo_cuenta,mes,anio):
    if 'username' in session:
        tipo_cuenta =int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes+'-'+anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s", [rut_contribuyente,tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                from registro_cv, contribuyente
                where (receptor=%s) and rut_contribuyente=emisor""", [contribuyentes[0][0]])
        compra_cv = cursor.fetchall()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                        from registro_cv, contribuyente
                        where (emisor=%s) and rut_contribuyente=receptor""", [contribuyentes[0][0]])
        venta_cv = cursor.fetchall()
        dtsUser = getContribuyente(cod_usuario[0])
        try:
            cursor.execute("""select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=4 and cod_tipo_cuenta=%s""",[rut_contribuyente,rut_contribuyente,tipo_cuenta])
            ctaBancariaSantanderEmpresa = cursor.fetchone()
            if ctaBancariaSantanderEmpresa:
                ###conciliacion compra
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                               from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                               where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                               and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.emisor
                               and receptor = %s
                               group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente
                               """, [ctaBancariaSantanderEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasCompras = cursor.fetchall()
                ### conciliacion ventas
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                               from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                               where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                               and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.receptor
                                               and emisor = %s
                                               group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente""",
                               [ctaBancariaSantanderEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasVentas = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                               [ctaBancariaSantanderEmpresa[0],desc_cartola])
                cartolaBancaria = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s",[ctaBancariaSantanderEmpresa[0]])
                cartolaHistorica = cursor.fetchall()
                cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                               [ctaBancariaSantanderEmpresa[0]])
                movimiento_cb = cursor.fetchall()
                if request.method == "GET":

                    return render_template("/bancos/bancoSantander.html", contribuyentes=contribuyentes,
                                           anio_actual=anio_actual, datosUsx=datosUsx, dtsUser=dtsUser,
                                           movimiento_cb=movimiento_cb,
                                           ctaBancariaSantanderEmpresa=ctaBancariaSantanderEmpresa,
                                           cartolaBancaria=cartolaBancaria,cartolaHistorica=cartolaHistorica,compra_cv=compra_cv,venta_cv=venta_cv,conciliacionesBancariasCompras=conciliacionesBancariasCompras,
                                           conciliacionesBancariasVentas=conciliacionesBancariasVentas)
                if 'saldos' in request.form:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.0.14:5001/saldo/santander/empresa'
                    payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                        ctaBancariaSantanderEmpresa[3], ctaBancariaSantanderEmpresa[4])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = ctaBancariaSantanderEmpresa[0]
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
                # if request.method == "POST":
                #     if tipo_cuenta == 3:
                #         anio = request.form["anio"]
                #         mes = request.form["mes"]
                #         desc_cartola = mes +'-'+anio
                #         cursor.execute(
                #             "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                #             [ctaBancariaSantanderEmpresa[0], desc_cartola])
                #         cartolaBancaria = cursor.fetchone()
                #         url_data = 'http://192.168.1.91:5001/cartola/santander/empresa'
                #         payload = '{"rut_a":"%s","pass":"%s","mes":"%s","anio":"%s"}' % (
                #             ctaBancariaSantanderEmpresa[3], ctaBancariaSantanderEmpresa[4],mes,anio)
                #
                #         headers = {
                #             'Content-Type': 'application/json'
                #         }
                #         response = requests.request("GET", url_data, headers=headers, data=payload)
                #         if response.status_code == 500:
                #             print("error en API")
                #         data = response.json()
                #         #######--------------------saldos-----------------------------------------------------------------
                #         url_data2 = 'http://192.168.1.91:5001/saldo/santander/empresa'
                #         payload2 = '{"rut_a":"%s","pass":"%s"}' % (
                #             ctaBancariaSantanderEmpresa[3], ctaBancariaSantanderEmpresa[4])
                #
                #         headers2 = {
                #             'Content-Type': 'application/json'
                #         }
                #         response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
                #
                #         if response2.status_code == 500:
                #             print("error en API")
                #         data2 = response2.json()
                #         try:
                #             if data:
                #                 if cartolaBancaria:
                #                     cursor.execute(
                #                         "delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                #                         [cartolaBancaria[0]])
                #                     print("cartola existe")
                #                     db.commit()
                #                     estado = False
                #                     for d in range(0, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         print(d)
                #                         estado = False
                #
                #                         for m in range(0, (len(movimiento_cb))):
                #                             if data[d]['n_documento'] in movimiento_cb[m][6]:
                #                                 estado = True
                #                                 print("exist not modified")
                #                         if estado == False:
                #                             cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                          cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                          values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                            data[d])
                #                             cod_movimiento_cb = cursor.fetchone()[0]
                #                             cursor.execute(
                #                                 """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                                 [ctaBancariaSantanderEmpresa[0], cod_movimiento_cb])
                #                             print(data[d])
                #                             success = 'actualizado'
                #                             flash(success)
                #                     db.commit()
                #                 else:
                #                     cursor.execute(
                #                         """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                #                         [desc_cartola, ctaBancariaSantanderEmpresa[0]])
                #                     cod_cartola_bancaria = cursor.fetchone()[0]
                #
                #                     for d in range(1, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                      cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                      values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                        data[d])
                #                         cod_movimiento_cb = cursor.fetchone()[0]
                #
                #                         cursor.execute(
                #                             """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                             [ctaBancariaSantanderEmpresa[0], cod_movimiento_cb])
                #                         print(data[d])
                #                     db.commit()
                #                     success = 'actualizado'
                #                     flash(success)
                #         except:
                #             db.rollback()
                #             print("error no esperado", sys.exc_info())
                #         try:
                #             if data2:
                #                 data2[0]['cod_cuenta_bancaria'] = ctaBancariaSantanderEmpresa[0]
                #                 cursor.execute(
                #                     """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                #                     data2[0])
                #             db.commit()
                #         except:
                #             db.rollback()
                #             success = 'error'
                #             flash(success)
                #             print("error no esperado", sys.exc_info())
        except:
            print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


@mod_bancos.route('/bancoBci/<rut_contribuyente>/<tipo_cuenta>/<mes>/<anio>', methods=["GET", "POST", "UPDATE"])
def bancoBci(rut_contribuyente,tipo_cuenta,mes,anio):
    if 'username' in session:
        tipo_cuenta = int(tipo_cuenta)
        cursor = db.cursor()
        anio_actual = t
        desc_cartola = mes +'-'+anio
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select rut_contribuyente from cuenta_bancaria where rut_apoderado =%s and cod_tipo_cuenta=%s", [rut_contribuyente,tipo_cuenta])
        rut_apoderado = cursor.fetchone()
        if not rut_apoderado:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
        else:
            cursor.execute("select * from contribuyente where rut_contribuyente = %s", [rut_apoderado])
            contribuyentes = cursor.fetchall()
        cursor.execute("select cod_usuario from usuario where nombre_usuario =%s ", [session['username']])
        cod_usuario = cursor.fetchone()
        dtsUser = getContribuyente(cod_usuario[0])
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
        from registro_cv, contribuyente
        where (receptor=%s) and rut_contribuyente=emisor""",[contribuyentes[0][0]])
        compra_cv = cursor.fetchall()
        cursor.execute("""select cod_registro_cv,receptor,emisor,fecha_emision,fecha_vencimiento,monto_total,estado_documento,nombre_contribuyente 
                from registro_cv, contribuyente
                where (emisor=%s) and rut_contribuyente=receptor""", [contribuyentes[0][0]])
        venta_cv = cursor.fetchall()

        try:
            cursor.execute(
                """select cod_cuenta_bancaria,rut_contribuyente,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,saldo_cuenta from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s and cod_banco=7 and cod_tipo_cuenta=%s""",
                [rut_contribuyente, rut_contribuyente, tipo_cuenta])
            ctaBancariaBciEmpresa = cursor.fetchone()

            if ctaBancariaBciEmpresa:
                ###conciliacion compra
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                               from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                               where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                               and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.emisor
                               and receptor = %s
                               group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente
                               """, [ctaBancariaBciEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasCompras = cursor.fetchall()
                ### conciliacion ventas
                cursor.execute("""select desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente ,SUM(COALESCE(cargo,0) + COALESCE(abono,0)) as p_total
                                               from movimiento_cb ,conciliacion ,registro_cv,contribuyente
                                               where movimiento_cb.cod_movimiento_cb = conciliacion.cod_movimiento_cb and conciliacion.cod_registro_cv = registro_cv.cod_registro_cv 
                                               and cod_cuenta_bancaria = %s and contribuyente.rut_contribuyente = registro_cv.receptor
                                               and emisor = %s
                                               group by desc_movimiento_cb,fecha_movimiento,fecha_movimiento,emisor,receptor,fecha_emision,fecha_vencimiento,monto_total,conciliacion.cod_movimiento_cb,nombre_contribuyente""",
                               [ctaBancariaBciEmpresa[0], contribuyentes[0][0]])
                conciliacionesBancariasVentas = cursor.fetchall()
                cursor.execute(
                    "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                    [ctaBancariaBciEmpresa[0], desc_cartola])
                cartolaBancaria = cursor.fetchall()
                cursor.execute("select * from cartola_bancaria where cod_cuenta_bancaria=%s",
                               [ctaBancariaBciEmpresa[0]])
                cartolaHistorica = cursor.fetchall()
                cursor.execute("select * from movimiento_cb where cod_cuenta_bancaria=%s",
                               [ctaBancariaBciEmpresa[0]])
                movimiento_cb = cursor.fetchall()
                if request.method == "GET":

                    return render_template("/bancos/bancoBci.html", contribuyentes=contribuyentes,
                                           anio_actual=anio_actual, datosUsx=datosUsx, dtsUser=dtsUser,
                                           movimiento_cb=movimiento_cb,
                                           ctaBancariaBciEmpresa=ctaBancariaBciEmpresa,
                                           cartolaBancaria=cartolaBancaria, cartolaHistorica=cartolaHistorica,compra_cv=compra_cv,venta_cv=venta_cv
                                           ,conciliacionesBancariasCompras=conciliacionesBancariasCompras,conciliacionesBancariasVentas=conciliacionesBancariasVentas)
                if 'saldos' in request.form:
                    #######--------------------saldos-----------------------------------------------------------------
                    url_data2 = 'http://192.168.0.14:5001/saldo/bci/empresario'
                    payload2 = '{"rut":"%s","pass":"%s"}' % (
                        ctaBancariaBciEmpresa[3], ctaBancariaBciEmpresa[4])

                    headers2 = {
                        'Content-Type': 'application/json'
                    }
                    response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)

                    if response2.status_code == 500:
                        print("error en API")
                    data2 = response2.json()
                    try:
                        if data2:
                            data2[0]['cod_cuenta_bancaria'] = ctaBancariaBciEmpresa[0]
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
                # if request.method == "POST":
                #     if tipo_cuenta == 8:
                #         anio = request.form["anio"]
                #         mes = request.form["mes"]
                #         desc_cartola = mes + '-' + anio
                #         cursor.execute(
                #             "select * from cartola_bancaria where cod_cuenta_bancaria=%s and desc_cartola_bancaria=%s",
                #             [ctaBancariaBciEmpresa[0], desc_cartola])
                #         cartolaBancaria = cursor.fetchone()
                #         url_data = 'http://192.168.0.14:5001/cartola/bci/empresario'
                #         payload = '{"rut":"%s","pass":"%s","mes":"%s","anio":"%s"}' % (
                #             ctaBancariaBciEmpresa[3], ctaBancariaBciEmpresa[4],mes,anio)
                #
                #         headers = {
                #             'Content-Type': 'application/json'
                #         }
                #         response = requests.request("GET", url_data, headers=headers, data=payload)
                #         if response.status_code == 500:
                #             print("error en API")
                #         data = response.json()
                #         #######--------------------saldos-----------------------------------------------------------------
                #         url_data2 = 'http://192.168.0.14:5001/saldo/bci/empresario'
                #         payload2 = '{"rut":"%s","pass":"%s"}' % (
                #             ctaBancariaBciEmpresa[3], ctaBancariaBciEmpresa[4])
                #
                #         headers2 = {
                #             'Content-Type': 'application/json'
                #         }
                #         response2 = requests.request("GET", url_data2, headers=headers2, data=payload2)
                #
                #         if response2.status_code == 500:
                #             print("error en API")
                #         data2 = response2.json()
                #         try:
                #             if data:
                #                 if cartolaBancaria:
                #                     cursor.execute("delete from movimiento_cb where cod_cartola_bancaria=%s and estado_bancaria='no conciliada'",
                #                                    [cartolaBancaria[0]])
                #                     print("cartola existe")
                #                     db.commit()
                #                     estado = False
                #                     for d in range(0, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cartolaBancaria[0]
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         print(d)
                #                         estado = False
                #
                #                         for m in range(0,(len(movimiento_cb))):
                #                             if data[d]['n_documento'] in movimiento_cb[m][6]:
                #                                 estado = True
                #                                 print("exist not modified")
                #                         if estado == False:
                #                             cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                          cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                          values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                            data[d])
                #                             cod_movimiento_cb = cursor.fetchone()[0]
                #                             cursor.execute(
                #                                 """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                                 [ctaBancariaBciEmpresa[0], cod_movimiento_cb])
                #                             print(data[d])
                #                             success = 'actualizado'
                #                             flash(success)
                #                     db.commit()
                #                 else:
                #                     cursor.execute(
                #                         """insert into cartola_bancaria (desc_cartola_bancaria,cod_cuenta_bancaria) values(%s,%s) returning cod_cartola_bancaria""",
                #                         [desc_cartola, ctaBancariaBciEmpresa[0]])
                #                     cod_cartola_bancaria = cursor.fetchone()[0]
                #
                #                     for d in range(1, len(data)):
                #                         data[d]['cod_cartola_bancaria'] = cod_cartola_bancaria
                #                         data[d]['estado_bancaria'] = 'no conciliada'
                #                         cursor.execute("""insert into movimiento_cb (desc_movimiento_cb,fecha_movimiento,num_documento,
                #                                      cargo,abono,cod_cartola_bancaria,estado_bancaria)
                #                                      values (%(descripcion)s,%(fecha)s,%(n_documento)s,%(cargo)s,%(abono)s,%(cod_cartola_bancaria)s,%(estado_bancaria)s) returning cod_movimiento_cb""",
                #                                        data[d])
                #                         cod_movimiento_cb = cursor.fetchone()[0]
                #
                #                         cursor.execute(
                #                             """update movimiento_cb set cod_cuenta_bancaria=%s where cod_movimiento_cb=%s""",
                #                             [ctaBancariaBciEmpresa[0], cod_movimiento_cb])
                #                         print(data[d])
                #                     db.commit()
                #                     success = 'actualizado'
                #                     flash(success)
                #         except:
                #             db.rollback()
                #             print("error no esperado", sys.exc_info())
                #         try:
                #             if data2:
                #                 data2[0]['cod_cuenta_bancaria'] = ctaBancariaBciEmpresa[0]
                #                 cursor.execute(
                #                     """update cuenta_bancaria set saldo_cuenta=%(saldo)s where cod_cuenta_bancaria=%(cod_cuenta_bancaria)s""",
                #                     data2[0])
                #             db.commit()
                #         except:
                #             db.rollback()
                #             success = 'error'
                #             flash(success)
                #             print("error no esperado", sys.exc_info())
        except:
            print("error no esperado", sys.exc_info())
        return render_template("/bancos/bancoBci.html", contribuyentes=contribuyentes,
                               anio_actual=anio_actual, datosUsx=datosUsx, dtsUser=dtsUser,compra_cv=compra_cv,venta_cv=venta_cv)
    return redirect('/auth/login')


@mod_bancos.route('/banco', methods=["GET", "POST", "UPDATE"])
def banco():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        anio_actual = t
        cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
        contribuyentes = cursor.fetchall()
        if request.method == 'GET':
            try:

                cursor.execute("select * from banco")
                bancos = cursor.fetchall()
                return render_template('/maestro/bancos.html', bancos=bancos, datosUsx=datosUsx,
                                       anio_actual=anio_actual,contribuyentes=contribuyentes)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json

                cursor.execute("insert into banco (nombre_banco,cod_sbif) values (%(nombre_banco)s,%(cod_sbif)s)",
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
                cursor = db.cursor()
                cursor.execute("update  banco set nombre_banco=%(nombre_banco)s where cod_banco=%(cod_banco)s", data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


