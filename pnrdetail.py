import pnrapi
from flask import Flask

# new app using flask
app = Flask(__name__)

@app.route('/')
def api_root():
    return 'Developed by sinwar'

@app.route('/pnr/<pnrnumber>')
def details(pnrnumber):
    p = pnrapi.PnrApi(pnrnumber) #10-digit PNR Number
    if p.request() == True:
        response = p.get_json()
        return response
    else:
        k = p.error
        return k
    