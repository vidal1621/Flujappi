import sys
from app.mod_auth.controllers import getDatosUsuario
from flask import Blueprint, session, render_template, request, redirect
from app import db, app, t

mod_documento = Blueprint('documento', __name__, url_prefix='/documento')


@mod_documento.route('/estadoDocumentos', methods=["GET", "POST", "UPDATE"])
def estadoDocumentos():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
        contribuyentes = cursor.fetchall()
        anio_actual = t
        if request.method == 'GET':
            try:

                cursor.execute("select * from estado_documento")
                estado_documento = cursor.fetchall()
                return render_template('/maestro/estadoDocumentos.html', estado_documento=estado_documento,
                                       anio_actual=anio_actual, datosUsx=datosUsx,contribuyentes=contribuyentes)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor.execute("insert into estado_documento(desc_estado_documento) values (%(desc_estado_documento)s)",
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
                cursor.execute(
                    "update  estado_documento set desc_estado_documento=%(desc_estado_documento)s where cod_estado_documento=%(cod_estado_documento)s",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


@mod_documento.route('/tipoConfiguracion', methods=["GET", "POST", "UPDATE"])
def tipoConfiguracion():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
        contribuyentes = cursor.fetchall()
        anio_actual = t
        if request.method == 'GET':
            try:

                cursor.execute("select * from tipo_configuracion")
                tipo_configuracion = cursor.fetchall()
                return render_template('/maestro/tipoConfiguracion.html', tipo_configuracion=tipo_configuracion,
                                       anio_actual=anio_actual, datosUsx=datosUsx,contribuyentes=contribuyentes)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json
                cursor.execute(
                    "insert into tipo_configuracion(desc_tipo_configuracion) values (%(desc_tipo_configuracion)s)",
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
                cursor.execute(
                    "update  tipo_configuracion set desc_tipo_configuracion=%(desc_tipo_configuracion)s where cod_tipo_configuracion=%(cod_tipo_configuracion)s",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')


@mod_documento.route('/tipoDocumentos', methods=["GET", "POST", "UPDATE"])
def tipoDocumentos():
    if 'username' in session:
        cursor = db.cursor()
        datosUsx = getDatosUsuario(session['username'])
        cursor.execute("select * from contribuyente where cod_usuario = %s", [datosUsx[0]])
        contribuyentes = cursor.fetchall()
        anio_actual = t
        if request.method == 'GET':
            try:

                cursor.execute("select * from tipo_documento")
                tipo_documento = cursor.fetchall()
                return render_template('/maestro/tipoDocumentos.html', tipo_documento=tipo_documento, datosUsx=datosUsx,
                                       anio_actual=anio_actual,contribuyentes=contribuyentes)
            except:
                print("error no esperado", sys.exc_info())
        elif request.method == 'POST':
            try:
                if request.content_type == 'application/json':
                    data = request.json

                cursor.execute(
                    "insert into tipo_documento (cod_tipo_documento,desc_tipo_documento) values (%(cod_tipo_documento)s,%(desc_tipo_documento)s)",
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
                    "update  tipo_documento set desc_tipo_documento=%(desc_tipo_documento)s where cod_tipo_documento=%(cod_tipo_documento)s",
                    data)
                db.commit()
                respuesta = 'ok'
                return respuesta
            except:
                print("error no esperado", sys.exc_info())
    return redirect('/auth/login')
