def extract_relevant_properties(test_geocode, test_timezone):
    relevant_properties = {
        'formatted_address': test_geocode.get('formatted_address'),
        'lat': test_geocode.get('geometry').get('location').get('lat'),
        'lng': test_geocode.get('geometry').get('location').get('lng'),
        'state_or_province': test_geocode.get('address_components')[-2].get('long_name'),
        'country': test_geocode.get('address_components')[-1].get('long_name'),
        'raw_offset': test_timezone.get('rawOffset'),
        'dst_offset': test_timezone.get('dstOffset'),
        'utc_offset': test_timezone.get('rawOffset') + test_timezone.get('dstOffset'),
        'tz_id': test_timezone.get('timeZoneId'),
        'tz_name': test_timezone.get('timeZoneName')
    }
    return relevant_properties

def check_location_properties(location, expected_properties):
    for key, value in expected_properties.items():
        assert location.__dict__[key] == value