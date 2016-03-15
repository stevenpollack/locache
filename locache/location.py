import os, googlemaps, math, warnings

class Location:

    google_api_key = os.environ.get('GOOGLE_API_KEY')
    if google_api_key is not None:
        gmaps = googlemaps.Client(key=google_api_key)
    else:
        warnings.warn("Environment variable 'GOOGLE_API_KEY' not found... gmaps object cannot be created.")
        gmaps = None

    def __init__(self, query, test_geocode_json=None, test_tz_json=None, test_datetime=None):

        if test_geocode_json is None:
            self.google_geocode = gmaps.geocode(query)[0]
            self.query = query
        else:
            self.google_geocode = test_geocode_json
            self.query = None

        # extract formatted address and (lat,lng)
        self.formatted_address = self.google_geocode.get('formatted_address')

        location = self.google_geocode.get('geometry').get('location')
        self.lat = location.get('lat')
        self.lng = location.get('lng')

        # extract country
        address_components = self.google_geocode.get('address_components')
        country_component = list(filter(lambda x: 'country' in x.get('types'), address_components))[0]
        self.country = country_component.get('long_name')

        # extract state/province
        state_component = list(filter(lambda x: 'administrative_area_level_1' in x.get('types'), address_components))[0]
        self.state_or_province = state_component.get('long_name')

        if test_tz_json is not None:
            self.google_tz = test_tz_json
        else:
            if test_datetime is not None:
                seconds_from_1970 = math.ceil(test_datetime.timestamp())
            else:
                seconds_from_1970 = math.ceil(datetime.utcnow().timestamp())

            self.google_tz = gmaps.timezone(location=','.join([self.lat, self.lng]),
                                            timestamp=seconds_from_1970)

        self.tz_id = self.google_tz.get('timeZoneId')
        self.tz_name = self.google_tz.get('timeZoneName')
        self.raw_offset = self.google_tz.get('rawOffset')
        self.dst_offset = self.google_tz.get('dstOffset')
        self.utc_offset = self.raw_offset + self.dst_offset