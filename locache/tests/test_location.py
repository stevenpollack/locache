from helper_functions import get_berlin_tz, extract_relevant_tz_properties,\
    extract_relevant_geocode_properties, check_location_properties
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

            location = Location(None,
                                timestamp=datetime(year=2016, month=5, day=11).timestamp(),
                                test_geocode_json=geocode_json,
                                test_tz_json=timezone_json)

            assert location.location is None
            check_location_properties(location,
                                      extract_relevant_geocode_properties(geocode_json))
            check_location_properties(location,
                                      extract_relevant_tz_properties(timezone_json))


    # do live integration test
    def test_gmaps_integration_passed_timestamp(self, test_json):
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

                # test JSON was created with 2016-5-11 as a timestamp for DST inference purposes.
                location = Location(query, timestamp=datetime(year=2016, month=5, day=11).timestamp())

                assert location.location == query
                check_location_properties(location,
                                          extract_relevant_geocode_properties(geocode_json))
                check_location_properties(location,
                                          extract_relevant_tz_properties(timezone_json))

    def test_gmaps_integration_no_timestamp(self, test_json):
        if os.environ.get('GOOGLE_API_KEY') is None:
            pass
        else:
            tests = {
                'Berlin, Germany': 0
            }

            for query, test_idx in tests.items():
                geocode_json = test_json[test_idx].get('geocode')
                timezone_json = test_json[test_idx].get('timezone')

                # test JSON was created with 2016-5-11 as a timestamp for DST inference purposes.
                location = Location(None, test_geocode_json=geocode_json)

                assert location.raw_offset == timezone_json.get('rawOffset')
                assert location.tz_id == timezone_json.get('timeZoneId')

                if get_berlin_tz() == 'CEST':
                    assert location.dst_offset == 3600
                    assert location.utc_offset == 7600
                    assert location.tz_name == "CEST"
                else:
                    assert location.dst_offset == 0
                    assert location.utc_offset == 3600
                    assert location.tz_name == "CET"


