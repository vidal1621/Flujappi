import sys
from app.mod_auth.controllers import getDatosUsuario
from flask import Blueprint, session, render_template, request, redirect
from app import db, app, t

mod_cuenta = Blueprint('cuenta', __name__, url_prefix='/cuenta')


@mod_cuenta.route('/tipoCuentas', methods=["GET", "POST", "UPDATE"])
def tipoCuentas():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
        contribuyentes = cursor.fetchall()
        anio_actual = t
        if request.method == 'GET':
            try:

                cursor.execute("select * from tipo_cuenta")
                tipo_cuenta = cursor.fetchall()
                cursor.execute("select * from banco")
                bancos = cursor.fetchall()
                return render_template('/maestro/tipoCuentas.html', tipo_cuenta=tipo_cuenta, datosUsx=datosUsx,
                                       bancos=bancos,
                                       anio_actual=anio_actual, contribuyentes=contribuyentes)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor.execute(
                    "insert into tipo_cuenta(desc_tipo_cuenta,cod_banco,estado_tipo_cuenta) values (%(desc_tipo_cuenta)s,%(cod_banco)s,%(estado_tipo_cuenta)s)",
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
                    "update  tipo_cuenta set desc_tipo_cuenta=%(desc_tipo_cuenta)s,cod_banco=%(cod_banco)s,estado_tipo_cuenta=%(estado_tipo_cuenta)s where cod_tipo_cuenta=%(cod_tipo_cuenta)s",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


@mod_cuenta.route('/planCuentas', methods=["GET", "POST", "UPDATE"])
def planCuentas():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        if request.method == 'GET':
            anio_actual = t
            cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
            contribuyentes = cursor.fetchall()
            titulo = 'Plan Cuentas'
            cursor.execute("select * from cuenta_gastos")
            cgastos = cursor.fetchall()
            return render_template('/maestro/planCuentas.html', datosUsx=datosUsx,
                                   anio_actual=anio_actual,
                                   contribuyentes=contribuyentes, titulo=titulo,cgastos=cgastos)
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                    cursor.execute(
                        """insert into cuenta_gastos (desc_cuenta_gastos,orden) values(%(desc_cuenta_gastos)s,
                        %(orden)s)""",
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
                    cursor.execute("""update cuenta_gastos set desc_cuenta_gastos=%(desc_cuenta_gastos)s ,orden=%(orden)s 
                                      where cod_cuenta_gastos=%(cod_cuenta_gastos)s  
                                    """,
                                   data)
                    db.commit()
                    respuesta = 'ok'
                    return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


@mod_cuenta.route('/listadoPendientes/', methods=["GET"])
def listadoPendientes():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("""select cod_cuenta_bancaria,rut_contribuyente,rut_apoderado,clave_bancaria,nombre_banco,desc_tipo_cuenta,estado_banco,estado_tipo_cuenta
        from cuenta_bancaria,banco,tipo_cuenta where estado_banco='no activa' or estado_tipo_cuenta='no activa'""")
        cuentasPendientes = cursor.fetchall()
        if request.method == 'GET':
            return render_template('/maestro/listadoPendientes.html',cuentasPendientes=cuentasPendientes,datosUsx=datosUsx)
    return redirect('/auth/login')


@mod_cuenta.route('/cuentasCorrientes/<rut_contribuyente>', methods=["GET", "POST", "UPDATE"])
def cuentasCorrientes(rut_contribuyente):
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        anio_actual = t
        if request.method == 'GET':
            cursor.execute("select * from contribuyente where rut_contribuyente=%s", [rut_contribuyente])
            contribuyentes = cursor.fetchall()
            cursor.execute("select * from cuenta_bancaria where rut_contribuyente = %s", [rut_contribuyente])
            cuenta_bancaria = cursor.fetchall()
            cursor.execute("select * from tipo_cuenta")
            tipo_cuenta = cursor.fetchall()
            cursor.execute("select * from banco")
            banco = cursor.fetchall()
            dtsctas = []
            if cuenta_bancaria:
                try:
                    for c in range(len(list(cuenta_bancaria))):
                        cursor.execute(
                            "select desc_tipo_cuenta,nombre_banco,desc_cuenta_bancaria from cuenta_bancaria,tipo_cuenta,banco where rut_contribuyente=%s and tipo_cuenta.cod_tipo_cuenta = %s and banco.cod_banco =%s"
                            , [rut_contribuyente, cuenta_bancaria[c][9], cuenta_bancaria[c][6]])
                        dtsCbts = cursor.fetchone()
                        obgDatos = {
                            'tipo cuenta': dtsCbts[0],
                            'banco': dtsCbts[1],
                            'numero cuenta': dtsCbts[2]
                        }
                        dtsctas.append(obgDatos)
                except:
                    print("error no esperado", sys.exc_info())

            return render_template('/maestro/cuentasCorrientes.html', datosUsx=datosUsx,
                                   cuenta_bancaria=cuenta_bancaria,
                                   anio_actual=anio_actual, dtsctas=dtsctas, tipo_cuenta=tipo_cuenta, banco=banco,
                                   contribuyentes=contribuyentes)
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor.execute(
                    """insert into cuenta_bancaria (desc_cuenta_bancaria,cod_banco,rut_apoderado,clave_bancaria,cod_tipo_cuenta,rut_contribuyente) values(%(desc_cuenta_bancaria)s,%(cod_banco)s,
                    %(rut_apoderado)s,%(clave_bancaria)s,%(cod_tipo_cuenta)s,%(rut_contribuyente)s)""",
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
                cursor.execute("""update cuenta_bancaria set desc_cuenta_bancaria=%(desc_cuenta_bancaria)s ,cod_banco=%(cod_banco)s ,
                rut_apoderado=%(rut_apoderado)s ,clave_bancaria=%(clave_bancaria)s ,cod_tipo_cuenta=%(cod_tipo_cuenta)s  where rut_contribuyente=%(rut_contribuyente)s  
                """,
                               data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')
