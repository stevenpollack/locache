from .location import Location, time_until_next
from flask import Response
import re, json, warnings


class Endpoint:
    response = None

    def create_cache_key(self, sep=":"):
        # strip weird tokens and white space from location
        self.normalized_location = re.sub('[ _!@#$%^&*():;\'",<.>/?=+\[\{\]\}\\\|]*', '', self.location).lower()
        self.cache_key = '%s%s%s' % (self.normalized_location, sep, self.timestamp)

    def __init__(self, location, timestamp, cache):
        self.mimetype = 'application/json'

        if location is None:
            self.response = Response(json.dumps({'msg': '`location` is a mandatory parameter.'}),
                                     status=400,
                                     mimetype=self.mimetype)
            return None

        if timestamp is not None:
            try:
                timestamp = int(timestamp)
            except ValueError as ve:
                warnings.warn(str(ve))
                status = 400
                self.response = Response(json.dumps({'msg': '`timestamp` must be a base-10 integer'}),
                                         status=400,
                                         mimetype=self.mimetype)
                return None

        self.location = location
        self.timestamp = timestamp
        self.cache = cache

        self.create_cache_key()

    def query_cache(self):
        # check to see if normalized location is available:
        # if it is, the location is crap
        cached_location = self.cache.get(self.normalized_location)
        if cached_location:
            warnings.warn("Retrieved bad location at key: %s" % self.normalized_location)
            self.response = Response(cached_location, status=400, mimetype=self.mimetype)
            return self.response

        # if the normalized location isn't available, then either:
        # 1. the location is good and has been cached (maybe with another timestamp), or
        # 2. we've never seen the location before
        cached_location = self.cache.get(self.cache_key)
        if cached_location:
            warnings.warn("Retrieved result cached at key: %s" % self.cache_key)

            # add timeUntilTomorrow to location_json before dehydration
            location_json = json.loads(cached_location)
            location_json['timeUntilTomorrow'] = time_until_next(0, 0, 0, self.Location.tz_id)
            self.response = Response(json.dumps(location_json), status=200, mimetype=self.mimetype)
            return self.response
        else:
            return None

    def fetch_info_and_populate_cache(self):
        # Location() will raise an AssertionError if google maps fails to
        # find anything for the location of interest. At this point, we
        # want to flag the location as "crap" by caching it by its normalized_location
        # and setting the key to the AssertionError's message. Since bad locations can
        # change in time, the expiration time is set to 7 days.
        try:
            self.Location = Location(self.location, self.timestamp)
            location_json = self.Location.to_json()

            # figure out expiration time for redis cache:
            # if a timestamp is provided, then there's no need to expire
            # the value; however, if no timestamp is provided, the cached
            # value depends on the UTC timestamp at the time of the GET
            # request, and therefore this should expire at the next instance
            # of 02:00, local time, since this is the next time DST may go
            # into effect
            if self.timestamp is not None:
                expiration_time = 0
            else:
                expiration_time = time_until_next(2, 0, 0, self.Location.tz_id)

            self.cache.set(self.cache_key, json.dumps(location_json), ex=expiration_time)
            # add timeUntilTomorrow to location_json before dehydration
            location_json['timeUntilTomorrow'] = time_until_next(0, 0, 0, self.Location.tz_id)
            self.response = Response(json.dumps(location_json), status=200, mimetype=self.mimetype)

        except AssertionError as ae:
            expiration_time = 7 * 24 * 60 * 60  # 7 days
            cached_value = json.dumps({'msg': str(ae)})
            self.cache.set(self.normalized_location, cached_value, ex=expiration_time)
            self.response = Response(cached_value, status=400, mimetype=self.mimetype)

        return self.response
