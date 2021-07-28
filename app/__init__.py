# Import flask and template operators
from datetime import date

from flask import Flask, render_template
from psycopg2 import connect
import sys

# Import SQLAlchemy

# Define the WSGI application object
app = Flask(__name__)
today = date.today()
t = today.strftime("%Y")  # Configurations
app.config.from_object('config')

db = connect(**app.config.get("DATABASE_CONNECT_OPTIONS"))

# Import a module / component using its blueprint handler variable (mod_auth)
from app.mod_auth.controllers import mod_auth
from app.mod_compra.controllers import mod_compra
from app.mod_venta.controllers import mod_ventas
from app.mod_bancos.controllers import mod_bancos
from app.mod_documento.controllers import mod_documento
from app.mod_cuenta.controllers import mod_cuenta
from app.mod_empresa.controllers import mod_empresa
from app.mod_cliente_proveedor.controllers import mod_cliente_proveedor
from app.mod_correo.controllers import mod_correo
from app.mod_reporte.controllers import mod_reporte
from app.mod_pagos.controllers import mod_pagos
from app.mod_pagos_webpay.controllers import mod_pagos_webpay


# Register blueprint(s)
app.register_blueprint(mod_auth)
app.register_blueprint(mod_compra)
app.register_blueprint(mod_ventas)
app.register_blueprint(mod_bancos)
app.register_blueprint(mod_documento)
app.register_blueprint(mod_cuenta)
app.register_blueprint(mod_empresa)
app.register_blueprint(mod_cliente_proveedor)
app.register_blueprint(mod_correo)
app.register_blueprint(mod_reporte)
app.register_blueprint(mod_pagos)
app.register_blueprint(mod_pagos_webpay)
