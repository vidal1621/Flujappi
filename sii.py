import requests
import psycopg2
from psycopg2 import connect
from datetime import datetime


cnx = connect(
    database='xeeffy',
    host='190.114.254.146',
    port='5432',
    user='christian',
    password='1020')


cursor = cnx.cursor()
cursor.execute("select * from entidad where password_sii is not null")
entidad = cursor.fetchall()
if entidad:
    for e in range(len(list(entidad))):
        rutdvr = entidad[e][0]
        dv = rutdvr.split(sep="-", maxsplit=2)
        dvr = dv[1]
        rut = dv[0].replace('.', '')
        clave = entidad[e][27]
        date = datetime.now()
        year_month = date.strftime('%Y%m')
        month = date.strftime('%m')

        url = "http://dte2.xdte.cl:1528/get_compras"
        url2 = "http://dte2.xdte.cl:1528/get_ventas"
        payload = '{"rut":"%s","dv":"%s","pas":"%s","periodo":"%s"}'%(rut,dvr,clave,year_month)

        # payload = {"\"rut\":\"rut\",\"dv\":\"dvr\",\"pas\":\"clave\",\"periodo\":\"periodo\""}

        headers = {
            'Content-Type': 'application/json'
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        if response.status_code == 500:
            print("error DB")

        try:
            mounth_month = date.strftime('%m')
            year_month = date.strftime('%Y')
            response2 = requests.request("GET", url2, headers=headers, data=payload)
            data2 = response.json()
            data3 = response2.json()
            if data2:
                cursor.execute("delete from registro_compra_venta where anio =%s and mes =%s and cod_entidad=%s", [year_month, mounth_month,entidad[e][0]])
                cnx.commit()
                for d in range(len(data2['REGISTRO'])):
                    dte = data2['REGISTRO'][d]['dte']
                    emisor = data2['REGISTRO'][d]['emisor']
                    fecha = data2['REGISTRO'][d]['fecha']
                    iva = data2['REGISTRO'][d]['iva']
                    fecha_sii = data2['REGISTRO'][d]['fecha_sii']
                    fecha_sii = fecha_sii[0:10]
                    if fecha_sii:
                        mesR = fecha_sii.split(sep="/", maxsplit=2)
                        mesRip = mesR[1]
                        if mesRip == mounth_month:
                            mesRip = mesR[1]
                        else:
                            mesRip = '00'
                    elif fecha_sii == '':
                        mesR = fecha.split(sep="/", maxsplit=2)
                        mesRip = mesR[1]
                        if mesRip == mounth_month:
                            mesRip = mesR[1]
                        else:
                            mesRip = '00'

                    neto = data2['REGISTRO'][d]['neto']
                    razon_social = data2['REGISTRO'][d]['razonSocial']
                    total = data2['REGISTRO'][d]['total']
                    excento = data2['REGISTRO'][d]['exento']
                    folio = data2['REGISTRO'][d]['Folio']
                    cod_entidad = rutdvr

                    cursor.execute("""insert into registro_compra_venta (desc_registro_compra_venta,emisor,dte,folio,fecha,receptor,excento,neto,iva,total,usuario,cod_entidad,anio,mes)
                     values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_compra_venta""",
                                   ['compra', emisor, dte, folio, fecha, cod_entidad, excento or 0, neto or 0, iva or 0,
                                    total or 0, razon_social, cod_entidad, year_month, mesRip])
                    print("compras guardadas con exito")
                    cnx.commit()
                for d in range(len(data3['NO_INCLUIR'])):
                    dte = data3['NO_INCLUIR'][d]['dte']
                    emisor = data3['NO_INCLUIR'][d]['emisor']
                    fecha = data3['NO_INCLUIR'][d]['fecha']

                    iva = data3['NO_INCLUIR'][d]['iva']
                    fecha_sii = data3['NO_INCLUIR'][d]['fecha_sii']
                    if fecha_sii:
                        mesR = fecha_sii.split(sep="/", maxsplit=2)
                        mesRip = mesR[1]
                        if mesRip == mounth_month:
                            mesRip = mesR[1]
                        else:
                            mesRip = '00'
                    elif fecha_sii == '':
                        mesR = fecha.split(sep="/", maxsplit=2)
                        mesRip = mesR[1]
                        if mesRip == mounth_month:
                            mesRip = mesR[1]
                        else:
                            mesRip = '00'
                    neto = data3['NO_INCLUIR'][d]['neto']
                    razon_social = data3['NO_INCLUIR'][d]['razonSocial']
                    total = data3['NO_INCLUIR'][d]['total']
                    excento = data3['NO_INCLUIR'][d]['exento']
                    folio = data3['NO_INCLUIR'][d]['Folio']
                    cursor.execute("""insert into registro_compra_venta (desc_registro_compra_venta,emisor,dte,folio,fecha,receptor,excento,neto,iva,total,usuario,cod_entidad,anio,mes)
                                             values (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING cod_registro_compra_venta""",
                                   ['venta', emisor, dte, folio, fecha, cod_entidad, excento or 0, neto or 0,
                                    iva or 0, total or 0, razon_social, cod_entidad, year_month, mesRip])
                    print("ventas guardadas con exito")
                    cnx.commit()
                print("se guardaron archivos correctamente")
        except:
            print("error no esperado")