import os, googlemaps, warnings, pytz, json
from datetime import datetime

class Location:
    # initialize certain properties
    gmaps = None
    location = None
    city = None
    state_or_province = None
    country = None

    def __init__(self,
                 location,
                 timestamp=None,
                 google_api_key=os.environ.get('GOOGLE_API_KEY'),
                 test_geocode_json=None,
                 test_tz_json=None):
        """
        :param location: a string indicating the query to be sent to google maps. The first
          result returned by google maps will be used; however this argument will be ignored
          if `test_geocode_json` is not None.
        :param timestamp: the number of seconds since 1970-01-01 00:00 UTC in local time.
          This is used to have google maps determine daylight savings; however this argument
          will be ignored inf `test_tz_json` is not None.
        :param google_api_key: api key for google maps API.
        :param test_geocode_json: object that's meant to mimic the structure of a successful
          response from the google maps Geocode API.
        :param test_tz_json:  object that's meant to mimic the structure of a successful
          response from the google maps Timezone API
        :return:
        """

        if google_api_key is not None:
            gmaps = googlemaps.Client(key=google_api_key)
        else:
            warnings.warn("Environment variable 'GOOGLE_API_KEY' not found... gmaps object cannot be created.")

        if test_geocode_json is None:
            try:
                self.google_geocode = gmaps.geocode(location)[0]
                self.location = location
            except IndexError:
                raise AssertionError('Google maps returned no results for location: %s' % location)
        else:
            self.google_geocode = test_geocode_json

        # extract formatted address and (lat,lng)
        self.formatted_address = self.google_geocode.get('formatted_address')

        # overwrite input variable 'location'
        location = self.google_geocode.get('geometry').get('location')
        self.lat = location.get('lat')
        self.lng = location.get('lng')

        # extract city, state/province, and country
        address_components = self.google_geocode.get('address_components')

        for component in address_components:
            component_types = component.get('types')
            if all([type in component_types for type in ['locality', 'political']]):
                self.city = component.get('long_name')

            if all([type in component_types for type in ['administrative_area_level_1', 'political']]):
                self.state_or_province = component.get('long_name')

            if all([type in component_types for type in ['country', 'political']]):
                self.country = component.get('long_name')

        self.timestamp = timestamp

        if test_tz_json is not None:
            self.google_tz = test_tz_json
        else:
            self.google_tz = gmaps.timezone(location=','.join([str(self.lat), str(self.lng)]),
                                            timestamp=self.timestamp)

        self.tz_id = self.google_tz.get('timeZoneId')
        self.raw_offset = self.google_tz.get('rawOffset')

        if timestamp is not None:
            self.tz_name = self.google_tz.get('timeZoneName')
            self.dst_offset = self.google_tz.get('dstOffset')
            self.utc_offset = self.raw_offset + self.dst_offset
            self.utc_from_timestamp = datetime.utcfromtimestamp(timestamp)
        else:
            self.utc_from_timestamp = datetime.utcnow()
            # infer timezone information from the local time....
            # this can lead to certain errors for ambiguously defined times
            try:
                local_time = pytz.timezone(self.tz_id).localize(datetime.now())
                self.utc_offset = int(local_time.utcoffset().total_seconds())
                self.dst_offset = self.utc_offset - self.raw_offset
                self.tz_name = local_time.tzname()
            except pytz.exceptions.AmbiguousTimeError:
                warnings.warn('pytz.exceptions.AmbiguousTimeError: %s %s' % (datetime.now(), self.tz_id))
                self.tz_name = self.google_tz.get('timeZoneName')
                self.dst_offset = self.google_tz.get('dstOffset')
                self.utc_offset = self.raw_offset + self.dst_offset

    def to_json(self):
        output = {
            'formattedAddress': self.formatted_address,
            'lat': self.lat,
            'lng': self.lng,
            's': self.state_or_province,
            'country': self.country,
            'city': self.city,
            'rawOffset': self.raw_offset,
            'dstOffset': self.dst_offset,
            'utcOffset': self.utc_offset,
            'timeZoneId': self.tz_id,
            'timeZoneName': self.tz_name,
            'utcFromTimestamp': self.utc_from_timestamp.strftime("%Y-%m-%d %H:%M:%S UTC")
        }

        return json.dumps(output)