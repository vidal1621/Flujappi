import random
import string
import smtplib
import sys
from datetime import datetime, time, timedelta
import flask
import transbank
from flask import Blueprint, render_template, request, flash, redirect, session
from transbank.oneclick.mall_inscription import MallInscription
from transbank.onepay import IntegrationType
from app.mod_pagos_webpay.controllers import webpay_plus_create
from app import db
import pyrebase


mod_auth = Blueprint('auth', __name__, url_prefix='')
configFirebase = {
    "apiKey": "AIzaSyCgPzRY_jHfLZwg-jblC9rKfPXosQruNJU",
    "authDomain": "flujappi.firebaseapp.com",
    "projectId": "flujappi",
    "storageBucket": "flujappi.appspot.com",
    "messagingSenderId": "313088215504",
    "appId": "1:313088215504:web:212be06619f0d6f11c11d5",
    "measurementId": "G-Y10LZSYYS8",
    "databaseURL": "https://flujappi-default-rtdb.firebaseio.com/"
}
firebase = pyrebase.initialize_app(configFirebase)
auth = firebase.auth()


@mod_auth.route('/', methods=['GET'])
def index():
    return render_template("/flujappy.cl/index.html")


@mod_auth.route('/auth/pago/', methods=['GET'])
def pago():
    cursor = db.cursor()
    cursor.execute("select cod_usuario,nombre_usuario from usuario where nombre_usuario=%s",[session['username']])
    cod_usuario = cursor.fetchone()
    if request.method == "GET":
        return render_template('/auth/pago.html',cod_usuario=cod_usuario)


@mod_auth.route('/auth/login/', methods=['GET', 'POST'])
@mod_auth.route('/login/', methods=['GET', 'POST'])
def login():
    cursor = db.cursor()
    if request.method == "GET":
        return render_template("/auth/login.html")
    if request.method == "POST":
        try:

            email = request.form["email"]
            password = request.form["password"]
            try:
                user = auth.sign_in_with_email_and_password(email, password)
            except:
                flash("contrasena incorrecta")
                return redirect("/login")
            cursor.execute("select token,nombre_usuario,cod_usuario from usuario where mail_usuario =%s",[email])
            token = cursor.fetchone()
            cursor.execute("select cod_pagos,desc_pagos,fecha_pagos,fecha_expiracion,estado_pagos,cod_usuario,voucher_transbank from pagos where cod_usuario =%s and estado_pagos='pagado'",[token[2]])
            estado_pagos = cursor.fetchone()
            if estado_pagos:
                fecha_hoy = datetime.now().date()
                if fecha_hoy < estado_pagos[3]:
                    if token:
                        if user['localId'] == token[0]:
                            session['username'] = token[1]
                            flash("correcto")
                            return redirect("/empresa/seleccionarEmpresa")
                        else:
                            flash("error usuario no existe token no valido")
                            return redirect("/login")
                    else:
                        print("no tiene token")
                else:
                    flash("expirada")

                    return redirect("/auth/pago")
            else:
                flash("sinpagos")
                return redirect("/auth/pago")
        except:
            flash("error")
            return redirect("/login")


@mod_auth.route('/suscribirse/', methods=['GET', 'POST'])
def suscribirse():
    cursor = db.cursor()
    if request.method == "POST":
        mensaje = request.form["mensaje"]
        email = request.form["email"]
        nombre = request.form["nombre"]
        celular = request.form["celular"]
        estado = 'pendiente'
        try:
            cursor.execute("insert into clientes_prospectos (desc_clientes_prospectos,email,nombre,celular,estado) values (%s,%s,%s,%s,%s)",
                           [mensaje,email,nombre,celular,estado])
            db.commit()
            flash("ok")
        except:
            flash("error")
            return render_template("/auth/suscribirse.html")
    return render_template("auth/suscribirse.html")


@mod_auth.route('/maestroSuscribirse/', methods=['GET', 'POST'])
def maestroSuscribirse():
    cursor = db.cursor()
    cursor.execute("select * from clientes_prospectos")
    tickets = cursor.fetchall()
    datosUsx = getDatosUsuario(session['username'])
    if request.method == "POST":
        estado = request.form["estado"]
        codigo = request.form["codigo"]
        try:
            cursor.execute("update clientes_prospectos set estado=%s where cod_clientes_prospectos=%s ",[estado,codigo])
            db.commit()
            flash("ok")
        except:
            flash("error")
            return render_template("/auth/maestroSuscribirse.html")
    return render_template("auth/maestroSuscribirse.html",tickets=tickets,datosUsx=datosUsx)


@mod_auth.route('/logout/', methods=['GET', 'POST'])
def logout():
    auth.current_user = None
    session.pop('username', None)
    flash("cerrada")
    return redirect("/login")


@mod_auth.route('/signup/', methods=['GET', 'POST'])
def signup():
    cursor = db.cursor()
    if request.method == "GET":
        return render_template("/auth/signup.html")
    if request.method == "POST":
        try:
            email = request.form["email"]
            password = request.form["password"]
            confirmPass = request.form["confirmPassword"]
            if password == confirmPass:
                user = auth.create_user_with_email_and_password(email, password)
                mauth  = user['localId']
                try:
                    cursor.execute("insert into usuario (nombre_usuario,mail_usuario,pass_usuario,token) values (%s,%s,%s,%s)",[email,email,password,mauth])
                    db.commit()
                except:
                    db.rollback()

                flash("correcto")
                return redirect("/login")
            else:
                flash("incorrect")
                return render_template("/auth/signup.html")

        except:
            flash("error")
            return render_template("/auth/signup.html")


@mod_auth.route('/olvidoPass/', methods=['GET', 'POST'])
def olvidoPass():
    cursor = db.cursor()
    if request.method == "POST":
        email = request.form["email"]
        if email:
            cursor.execute("select * from usuario where mail_usuario=%s",[email])
            exist = cursor.fetchone()
            if exist:
                auth.send_password_reset_email(exist[5])
                flash("restablecer password")
                return redirect("/login")
            else:
                flash("correo no existe")
                return render_template("/auth/olvidoPass.html")
    if request.method == "GET":
        return render_template("/auth/olvidoPass.html")



def getContribuyente(cod_usuario):
    cursor = db.cursor()
    cursor.execute("select rut_contribuyente,nombre_contribuyente,clave_tributaria from contribuyente where cod_usuario=%s", [cod_usuario])
    dtsUser = cursor.fetchall()
    return dtsUser


def getCuentaContribuyente(rut_contribuyente):
    cursor = db.cursor()
    cursor.execute(
        "select cod_tipo_cuenta,rut_contribuyente,rut_apoderado from cuenta_bancaria where rut_contribuyente=%s or rut_apoderado=%s",
        [rut_contribuyente,rut_contribuyente])
    codCuenta = cursor.fetchall()
    return codCuenta


def getDatosUsuario(nombre_usuario):
    try:
        cursor = db.cursor()
        cursor.execute("select cod_usuario,nombre_usuario,mail_usuario,pass_usuario,desc_perfil_usuario from usuario,perfil_usuario where nombre_usuario =%s and usuario.cod_perfil_usuario = perfil_usuario.cod_perfil_usuario",
                       [nombre_usuario])
        datosUser = cursor.fetchone()
        return datosUser
    except:
        print("error no esperado", sys.exc_info())

def CRut(rut):
    if rut == "":
        return rut
    rut = str.replace(rut, ".", "")
    rut = str.replace(rut, "-", "")
    rut = "0000000000" + rut
    l = len(rut)
    rut_aux = "-" + rut[l - 1:l]
    l = l - 1
    while 2 < l:
        rut_aux = "." + rut[l - 3:l] + rut_aux
        l = l - 3

    rut_aux = rut[0:l] + rut_aux
    l = len(rut_aux)
    rut_aux = rut_aux[l - 12:l]
    return rut_aux

def __build_dict(description, row):
    res = {}
    for i in range(len(description)):
        res[description[i][0]] = row[i]
    return res


def myconverter(o):
    if isinstance(o, datetime):
        return o.__str__()


def dictfetchall(cursor):
    res = []
    rows = cursor.fetchall()
    for row in rows:
        res.append(__build_dict(cursor.description, row))
    return res


@mod_auth.route('/actualizar/', methods=['GET'])
def actualizar():
    from app.mod_bancos.controllers import actualizarBanco
    from app.mod_compra.controllers import actualizarCompras
    from app.mod_empresa.controllers import saldosEmpresas
    from app.mod_venta.controllers import actualizarVentas
    cursor = db.cursor()
    cursor.execute("select * from solicitudes where estado='procesando' limit 5")
    proccess = cursor.fetchall()
    for solicitud in range(len(list(proccess))):

        try:
            cod_solicitud = proccess[solicitud][7]
            cursor.execute("update solicitudes set estado='proceso' where cod_solicitudes =%s",[cod_solicitud])
            #ejecutar acciones
            if proccess[0][0] == 'saldos empresas':
                saldosEmpresas(proccess[solicitud][2])
            if proccess[0][0] == 'ventas':
                actualizarVentas(proccess[solicitud][2], proccess[solicitud][5], proccess[solicitud][6])
            if proccess[0][0] == 'compras':
                actualizarCompras(proccess[solicitud][2], proccess[solicitud][5], proccess[solicitud][6])
            if proccess[0][0] == 'solicitud':
                actualizarBanco(proccess[solicitud][2], proccess[solicitud][3],proccess[solicitud][6], proccess[solicitud][5],proccess[solicitud][8],proccess[solicitud][9],solicitud[solicitud][10])
            cursor.execute("update solicitudes set estado='terminado' where cod_solicitudes =%s", [cod_solicitud])
            db.commit()
        except:
            print("error no esperado", sys.exc_info())
            db.rollback()

