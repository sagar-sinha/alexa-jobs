import requests

class Github:
    @staticmethod
    def get_jobs(query=None, location=None):
        url = 'https://jobs.github.com/positions.json'

        params = {
            'description': query,
            'location': location
        }

        r = requests.get(url, params=params)

        return r.json()
