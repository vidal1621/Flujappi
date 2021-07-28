import sys
from app.mod_auth.controllers import getDatosUsuario
from flask import Blueprint, session, render_template, request, redirect
from app import db, app, t

mod_pagos = Blueprint('pagos', __name__, url_prefix='/pagos')

from transbank.error.transbank_error import TransbankError
from transbank.oneclick.request import MallTransactionAuthorizeDetails
from flask import render_template, request
from transbank.oneclick.mall_inscription import MallInscription
from transbank.oneclick.mall_transaction import MallTransaction
import random


@mod_pagos.route('start', methods=['GET'])
def show_start():
    user_name = 'christian'
    email = 'prueba@gmail.com'
    return start(user_name,email)


@mod_pagos.route('status', methods=['GET'])
def show_status():
    return render_template('/oneclick/status_form.html')


@mod_pagos.route('start/<user_name>/<email>', methods=['POST'])
def start(user_name, email):
    response_url = 'http://192.168.0.16:8888/pagos/finish'
    resp = MallInscription.start(
        user_name=user_name,
        email=email,
        response_url=response_url)
    return render_template('oneclick/started.html', resp=resp, req=request.form)


@mod_pagos.route('/finish', methods=['POST'])
def finish():
    req = request.form
    token = request.form.get('TBK_TOKEN')
    resp = MallInscription.finish(token=token)
    buy_order = str(random.randrange(1000000, 99999999))
    commerce_code_1 = '597055555542'
    amount = 300
    username = 'username'
    return authorize(resp.tbk_user,username,buy_order,commerce_code_1,amount)


@mod_pagos.route('authorize/<tbk_user>/<user_name>/<buy_order>/<commerce_code>/<amount>/', methods=['POST'])
def authorize(tbk_user,user_name,buy_order,commerce_code,amount):
    installments_number = 1
    # req = request.form
    # tbk_user = request.form.get('tbk_user')
    # user_name = request.form.get('user_name')
    # buy_order = request.form.get('buy_order')
    # token_inscription = request.form.get('token_inscription')
    #
    # commerce_code = request.form.get('details[0][commerce_code]')
    # buy_order_child = request.form.get('details[0][buy_order]')
    # installments_number = request.form.get('details[0][installments_number]')
    # amount = request.form.get('details[0][amount]')
    #
    # commerce_code2 = request.form.get('details[1][commerce_code]')
    # buy_order_child2 = request.form.get('details[1][buy_order]')
    # installments_number2 = request.form.get('details[1][installments_number]')
    # amount2 = request.form.get('details[1][amount]')

    details = MallTransactionAuthorizeDetails(commerce_code, installments_number, 1,amount)

    resp = MallTransaction.authorize(user_name=user_name, tbk_user=tbk_user, buy_order=buy_order, details=details)
    return render_template('oneclick/refund.html', req=req, resp=resp, details=details.details, buy_order=buy_order,
                           tbk_user=tbk_user)


@mod_pagos.route('refund', methods=['POST'])
def refund():
    req = request.form
    buy_order = request.form.get('buy_order')
    child_commerce_code = request.form.get('child_commerce_code')
    child_buy_order = request.form.get('child_buy_order')
    amount = request.form.get('amount')
    tbk_user = request.form.get('tbk_user')

    resp = MallTransaction.refund(buy_order, child_commerce_code, child_buy_order, amount)
    return render_template('oneclick/delete.html', req=req, resp=resp, tbk_user=tbk_user)


@mod_pagos.route('delete', methods=['POST'])
def delete():
    req = request.form

    tbk_user = request.form.get('tbk_user')
    user_name = request.form.get('user_name')

    try:
        resp = MallInscription.delete(tbk_user, user_name)
        return render_template('oneclick/deleted.html', req=req, resp=resp)
    except TransbankError as e:
        print("ERROR_MESSAGE: {}".format(e.message))


@mod_pagos.route('status', methods=['POST'])
def status():
    buy_order = request.form.get('buy_order')

    resp = MallTransaction.status(buy_order)

    return render_template('oneclick/status.html', resp=resp, req=request.form)