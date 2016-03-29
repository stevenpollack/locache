import os, redis
from flask import Flask, redirect, request
from locache.root import Endpoint

r = redis.from_url(os.environ.get('REDIS_URL'))

app = Flask(__name__)

@app.route('/info')
def info():
    return """
    <p>main-endpoint:
     <a href='/'>
        locache.herokuapp.com/?{location[, timestamp]}
     </a>
    </p>
    <p>docs (apiary.io):
     <a href='/docs'>
        locache.herokuapp.com/docs
     </a>
    </p>
    <p>github:
     <a href='https://github.com/stevenpollack/locache'>
        https://github.com/stevenpollack/locache
     </a>
    </p>
    """


@app.route('/docs')
def route_to_apiary():
    apiary_io = 'http://docs.locache.apiary.io/'
    return redirect(apiary_io, code=302)

@app.route('/', methods=['GET'])
def get_tz_info():

    if len(request.args) == 0:
        return redirect('/info')

    location = request.args.get('location')
    timestamp = request.args.get('timestamp')

    endpoint = Endpoint(location, timestamp, r)

    if endpoint.query_cache():
        return endpoint.response

    return endpoint.fetch_info_and_populate_cache()



if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0', port=5000)
