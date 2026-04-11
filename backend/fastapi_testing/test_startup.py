from fastapi.testclient import TestClient
from startup import app

client=TestClient(app)

def test_get_user():
    _url = 'https://127.0.0.1:8000/user/'
    pay_load={ "id":2,
            "name":"john",
            "email":"nick@gmail.com",
            "company":"abc"
    }
    _response=client.post(url=_url,json=pay_load)
    
    
    # cases
    assert _response.status_code==200
    assert _response.json()['company'] == 'abc'
    assert _response.status_code != 422     
