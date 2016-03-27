import pytz
from datetime import datetime

def extract_relevant_geocode_properties(test_geocode):
    # the position of the address_component features is hard coded, and thus
    # you may have to manipulate geocode json in order to make your certain city,
    # state/province, or country line up...
    relevant_properties = {
        'formatted_address': test_geocode.get('formatted_address'),
        'lat': test_geocode.get('geometry').get('location').get('lat'),
        'lng': test_geocode.get('geometry').get('location').get('lng'),
        'city': test_geocode.get('address_components')[0].get('long_name'),
        'state_or_province': test_geocode.get('address_components')[-2].get('long_name'),
        'country': test_geocode.get('address_components')[-1].get('long_name')
    }
    return relevant_properties

def extract_relevant_tz_properties(test_timezone):
    relevant_properties = {
        'raw_offset': test_timezone.get('rawOffset'),
        'dst_offset': test_timezone.get('dstOffset'),
        'utc_offset': test_timezone.get('rawOffset') + test_timezone.get('dstOffset'),
        'tz_id': test_timezone.get('timeZoneId'),
        'tz_name': test_timezone.get('timeZoneName')
    }
    return relevant_properties

def check_location_properties(location, expected_properties):
    for key, value in expected_properties.items():
        assert location.__dict__[key] == value, "failed to associate %s with %s" % (key, value)

# check whether berlin is currently in daylight savings
def get_berlin_tz():
    return pytz.timezone("Europe/Berlin").localize(datetime.now()).tzname()
