#!/usr/bin/env python
# -*- coding: utf-8 -*-

import smtplib
import sys

from flask import Blueprint, request, flash
from app import db, app, t
from email.mime.text import MIMEText

mod_correo = Blueprint('correo', __name__, url_prefix='/correo')


@mod_correo.route('/correos/<rut_contribuyente>/<monto>/<nombre>/<fecha>/<folio>/<correo>/<nombre_emisor>',
                  methods=['GET', 'POST'])
def correos(rut_contribuyente, monto, nombre, fecha, folio, correo, nombre_emisor):
    from_address = "Contacto@xeeffy.com"  # Dirección personal
    to_address = correo  # Destino
    html_variable = """Estimado(a): %s %s le informamos que se a emitido la factura con el folio %s ,la cual tiene como fecha de emsión %s y un monto de $ %s
    """%(rut_contribuyente,nombre,folio,fecha,monto)
    mime_message = MIMEText(html_variable, "html")
    mime_message["From"] = from_address
    mime_message["To"] = to_address
    mime_message["Subject"] = "Facturación Flujappy"
    server = smtplib.SMTP_SSL(host='mail.xeeffy.com', port=465)
    try:
        server.set_debuglevel(1)
        # server.starttls()
        # Login Credentials for sending the mail
        server.login(mime_message['From'], 'dacafe2020')
        # send the message via the server.
        server.sendmail(mime_message['From'], mime_message["To"], mime_message.as_string())
        server.quit()
        flash("correcto")
        return print("ok")
    except:
        print("error no esperado", sys.exc_info())
        success_message = """Error: el mensaje no pudo enviarse. 
                                                   """
        flash(success_message)
