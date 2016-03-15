from helper_functions import extract_relevant_properties, check_location_properties
from locache.location import Location
from datetime import datetime
import pytest, json, os

@pytest.fixture(scope = 'module')
def test_json():
    return json.load(open('locache/tests/test.json'))

class TestLocation:

    # check mocks:
    def test_location_properties(self, test_json):
        for idx in range(len(test_json)):
            geocode_json = test_json[idx]['geocode']
            timezone_json = test_json[idx]['timezone']

            expected_properties = extract_relevant_properties(geocode_json, timezone_json)
            location = Location(None, geocode_json, timezone_json)
            assert location.query is None
            check_location_properties(location, expected_properties)

    # do live integration test
    def test_gmaps_integration(self, test_json):
        if os.environ.get('GOOGLE_API_KEY') is None:
            pass
        else:
            tests = {
                'Berlin, Germany': 0,
                'Vancouver, Canada': 4
            }

            for query, test_idx in tests.items():
                geocode_json = test_json[test_idx].get('geocode')
                timezone_json = test_json[test_idx].get('timezone')
                expected_properties = extract_relevant_properties(geocode_json, timezone_json)

                # test JSON was created with 2016-5-11 as a timestamp for DST inference purposes.
                location = Location(query, test_datetime=datetime(year=2016, month=5, day=11))

                assert location.query == query
                check_location_properties(location, expected_properties)


