#!/usr/bin/env python

import json
import os
import firebase
import urllib3

from flask import Flask
from flask import make_response
from flask import request

# Flask app should start in global layout
app = Flask(__name__)

@app.route('/webhook', methods=['POST'])
def webhook():
    req = request.get_json(silent=True, force=True)

    print("Request:")
    print(json.dumps(req, indent=4))

    res = makeWebhookResult(req)

    res = json.dumps(res, indent=4)
    print(res)
    r = make_response(res)
    r.headers['Content-Type'] = 'application/json'
    return r


def makeWebhookResult(req):
    global speech
    action = req.get("result").get("action")

    if (action != "curso.valor") and (action != "translate.text") and (action != "planeta.temperatura"):
        return {}
    result = req.get("result")
    parameters = result.get("parameters")

    # Curso
    if action == "curso.valor":
        curso = parameters.get("curso")
        # cost = {'R': 100, 'Python': 200, 'Machine Learning': 300, 'Hadoop': 400}
        preco = 1
        from firebase import firebase
        firebase = firebase.FirebaseApplication('https://dsa-bot-teste-daec3.firebaseio.com', None)
        preco = firebase.get("/Cursos", curso + "/Preco")

        if curso:
            speech = "O preco do curso " + curso + " eh " + str(preco) + " Reais."
        else:
            speech = "Qual curso? escolha entre: " + str(preco.keys())

    # Traducao
    if action == "translate.text":
        text = parameters.get("text")
        lingua = parameters.get("lang-to")
        speech = text + " em " + lingua + " eh " + text[::-1]

    # Temperatura
    if action == "planeta.temperatura":
        planeta = parameters.get("planeta")
        if planeta != "Marte":
            speech = "Ainda nao medimos temperatura para " + planeta
        else:
            url = "http://marsweather.ingenology.com/v1/latest/?format=json"
            http = urllib3.PoolManager()
            r = http.request('GET', url)
            data = json.loads(r.data.decode('utf-8'))
            temperatura_minima = data.get("report").get("min_temp")
            temperatura_maxima = data.get("report").get("max_temp")
            speech = "Previsao para {}: minima de {} e maxima de {}".format(planeta, temperatura_minima, temperatura_maxima)

    print("Response:")
    print(speech)

    return {
        "speech": speech,
        "displayText": speech,
        # "data": {},
        # "contextOut": [],
        "source": "apiai-onlinestore-shipping"
    }

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))

    print("Starting app on port %d" % port)

    app.run(debug=True, port=port, host='0.0.0.0')
    #app.run(debug=True, port=port, host='127.0.0.1')
