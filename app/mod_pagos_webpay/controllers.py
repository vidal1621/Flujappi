import datetime
import random
import sys
import transbank
from flask import Blueprint, session, render_template, request, redirect, flash
from app import db, app, t
from flask import render_template, request
from transbank.error.transbank_error import TransbankError
from transbank.webpay.webpay_plus.transaction import Transaction, IntegrationType
from transbank.webpay.webpay_plus.deferred_transaction import DeferredTransaction, webpay_plus_deferred_commerce_code

mod_pagos_webpay = Blueprint('webpay', __name__, url_prefix='/webpay')


@mod_pagos_webpay.route("/create", methods=["POST", "GET"])
def webpay_plus_create():
    if 'username' in session:
        cursor = db.cursor()
        print("Webpay Plus Transaction.create")
        transbank.webpay.webpay_plus.webpay_plus_default_commerce_code = 597055555532
        # 579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C
        transbank.webpay.webpay_plus.default_api_key = "579B532A7440BB0C9079DED94D31EA1615BACEB56610332264630D42D0A36B1C"
        transbank.webpay.webpay_plus.default_integration_type = IntegrationType.TEST
        try:
            buy_order = request.form["buy_order"]
            session_id = request.form["session_id"]
            amount = request.form["amount"]
            return_url = request.url_root + 'webpay/commit'
            create_request = {
                "buy_order": buy_order,
                "session_id": session_id,
                "amount": amount,
                "return_url": return_url
            }
            response = Transaction.create(buy_order, session_id, amount, return_url)
            try:
                cursor.execute(
                    "insert into pagos (desc_pagos,estado_pagos,cod_usuario,monto,token)values (%s,%s,%s,%s,%s) RETURNING cod_pagos",
                    [buy_order, 'pendiente', session_id, amount, response.token])
                db.commit()
                cod_pagos = cursor.fetchone()[0]
                cursor.execute("select * from pagos where cod_pagos=%s", [cod_pagos])
                state = cursor.fetchone()
            except:
                db.rollback()
                print("error no esperado", sys.exc_info())
                return redirect("/login")
            print(response)
            if response.token == state[8]:
                return render_template('/plus/create.html', request=create_request, response=response)
            else:
                flash("errortoken")
                cursor.execute("delete from pagos where cod_pagos=%s", [state[0]])
                db.commit()
                return redirect("/login")
        except:
            print("error no esperado", sys.exc_info())
            return redirect("/login")
    return redirect("/login")


@mod_pagos_webpay.route("/commit", methods=["POST"])
def webpay_plus_commit():
    try:
        cursor = db.cursor()
        token = request.form.get("token_ws")
        print("commit for token_ws: {}".format(token))

        response = Transaction.commit(token=token)
        print("response: {}".format(response))
        data = {'vci': response.vci,
                'monto': response.amount,
                'estado': response.status,
                'orden': response.buy_order,
                'session_id': response.session_id,
                'tarjeta': response.card_detail,
                'date_account': response.accounting_date,
                'date': response.transaction_date,
                'codigo': response.authorization_code,
                'tipo_pago': response.payment_type_code,
                'response_code': response.response_code,
                'installments_number': response.installments_number}
        try:
            if data['estado'] == 'AUTHORIZED':
                sp = data['date'].split(sep="T")
                fecha_transacion = datetime.datetime.strptime(sp[0], "%Y-%m-%d")
                fecha_expiracion = fecha_transacion + datetime.timedelta(days=31)
                cursor.execute("select cod_usuario from pagos where desc_pagos=%s", [data['orden']])
                cod_usuario = cursor.fetchone()[0]
                cursor.execute("update pagos set estado_pagos='pagado' ,fecha_pagos=%s , fecha_expiracion=%s ,voucher_transbank=%s where cod_usuario=%s and estado_pagos=%s",
                               [fecha_transacion,fecha_expiracion,data['codigo'],cod_usuario,'pendiente'])
                db.commit()

                flash("exitoso")
                return redirect("/login")
            else:
                cursor.execute("delete from pagos where cod_usuario=%s and estado_pagos=%s ",
                               [data['session_id'], 'pendiente'])
                db.commit()
                flash("faltapago")
                return redirect("/login")
            return render_template('/plus/commit.html', token=token, response=response)
        except:
            cursor.execute("delete from pagos where cod_usuario=%s and estado_pagos=%s ",[data['session_id'],'pendiente'])
            db.commit()
            flash("faltapago")
            print("error no esperado", sys.exc_info())
            return redirect("/login")

    except:
        print("error no esperado", sys.exc_info())
        return redirect("/")


@mod_pagos_webpay.route("/refund", methods=["POST"])
def webpay_plus_refund():
    token = request.form.get("token_ws")
    amount = request.form.get("amount")
    print("refund for token_ws: {} by amount: {}".format(token, amount))

    try:
        response = Transaction.refund(token, amount)
        print("response: {}".format(response))

        return render_template("/plus/refund.html", token=token, amount=amount, response=response)
    except TransbankError as e:
        print(e.message)


@mod_pagos_webpay.route("refund-form", methods=["GET"])
def webpay_plus_refund_form():
    return render_template("/plus/refund-form.html")
