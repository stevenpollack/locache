import os, redis, re, warnings, json, pytz
from flask import Flask, redirect, request, Response
from locache.location import Location
from datetime import datetime, timedelta

r = redis.from_url(os.environ.get('REDIS_URL'))

app = Flask(__name__)

@app.route('/docs')
def route_to_apiary():
    apiary_io = 'http://docs.locache.apiary.io/'
    return (redirect(apiary_io, code=302))

def create_cache_key(location, timestamp, sep=":"):
    # strip weird tokens and white space from location
    normalized_location = re.sub('[ !@#$%^&*():;\'",<.>/?=+\[\{\]\}\\\|]*', '', location)
    return normalized_location, '%s%s%s' % (normalized_location, sep, timestamp)

@app.route('/', methods=['GET'])
def get_tz_info():
    location = request.args.get('location')
    timestamp = request.args.get('timestamp')
    mimetype = 'application/json'

    if location is None:
        status = 400
        return Response(json.dumps({'msg': '`location` is a mandatory parameter.'}),
                        status=400,
                        mimetype=mimetype)

    if timestamp is not None:
        try:
            timestamp = int(timestamp)
        except ValueError as ve:
            warnings.warn(str(ve))
            status = 400
            return Response(json.dumps({'msg': '`timestamp` must be a base-10 integer'}),
                            status=400,
                            mimetype=mimetype)

    # look up location in cache
    normalized_location, cache_key = create_cache_key(location, timestamp)

    # check to see if normalized location is available:
    # if it is, the location is crap
    cached_location = r.get(normalized_location)
    if cached_location:
        warnings.warn("Retrieved bad location at key: %s" % normalized_location)
        status = 400
        return Response(cached_location, status=status, mimetype=mimetype)

    # if the normalized location isn't available, then either:
    # 1. the location is good and has been cached (maybe with another timestamp), or
    # 2. we've never seen the location before
    cached_location = r.get(cache_key)
    if cached_location is None:
        try:
            location = Location(location, timestamp)
            cached_location = location.to_json()

            # figure out expiration time for redis cache
            if timestamp is not None:
                expiration_time = 0
            else:
                # calculate seconds until 02:00 local time
                local_tz = pytz.timezone(location.tz_id)
                local_time = local_tz.localize(datetime.now())

                if local_time.hour < 2:
                    td = timedelta(days=0)
                else:
                    td = timedelta(days=1)

                expiration_date = (local_time + td).replace(hour=2, minute=0, second=0)
                expiration_time = int((expiration_date - local_time).total_seconds())

            status = 200
        except AssertionError as ae:
            expiration_time = 7 * 24 * 60 * 60 # 7 days
            cache_key = normalized_location
            cached_location = json.dumps({'msg': str(ae)})
            status = 400
        finally:
            r.set(cache_key, cached_location, ex=expiration_time)
    else:
        warnings.warn("Retrieved result cached at key: %s" % cache_key)
        status = 200

    return Response(cached_location, status=status, mimetype=mimetype)


if (__name__ == '__main__'):
    app.run(debug=True, host='0.0.0.0', port=5000)
