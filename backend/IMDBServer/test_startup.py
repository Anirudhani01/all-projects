import requests
from unittest import TestCase, main


class TestStartup(TestCase):
    def test_top_director_with_maximum_number_of_movie(self):
        _url = 'http://127.0.0.1:5000/top_director_with_maximum_number_of_movie/'
        _response = requests.get(url=_url)

        self.assertIn('top_director_with_maximum_number_of_movie', _response.text)
        self.assertIn('stanley kubrick', _response.text)
        self.assertEqual(_response.status_code, 200)
        self.assertNotEqual(_response.status_code, 404)


if __name__ == '__main__':
    main()