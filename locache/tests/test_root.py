import os, redis, json
from locache.slash import Endpoint

r = redis.from_url(os.environ.get('REDIS_URL'))

class TestEndpoint:

    def test_input(self):
        assert Endpoint(None, None, r).response.status_code == 400
        assert Endpoint('Berlin', 'se', r).response.status_code == 400
        assert Endpoint('Berlin', 123456789, r).response is None

    def test_cache_key_creation(self):
        endpoint = Endpoint('Berlin', 123456789, r)
        assert endpoint.cache_key == 'berlin:123456789'

        endpoint = Endpoint('Berlin!@#$%^&*()_+=,.<>/?;:\'\"[]{}\|', None, r)
        assert endpoint.cache_key == 'berlin:None'

    def test_cache_population(self):
        # find out location info for the Flat Iron building in NYC:
        # remove it from the cache if it already exists, then
        # go through sanity checks regarding the state of the Location
        # object after initialization...
        test_key = 'flatironbuilding:123456789'
        if r.get(test_key):
            r.delete(test_key)

        endpoint = Endpoint('Flatiron Building', 123456789, r)
        assert endpoint.cache_key == test_key

        # cache shouldn't hold any info on the object, so a query of
        # the cache should return None
        assert endpoint.query_cache() is None

        # a population of the cache should return a response object
        # and POPULATE the cache
        response = endpoint.fetch_info_and_populate_cache()
        assert response.status_code == 200

        assert r.get(endpoint.cache_key) is not None
        response_json = json.loads(response.get_data().decode())
        cached_info = json.loads(r.get(endpoint.cache_key).decode())
        for key, value in cached_info.items():
            assert response_json[key] == value

        assert response_json.get('timeUntilTomorrow') is not None
