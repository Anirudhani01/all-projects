import json
from fastapi import (FastAPI)

app=FastAPI()

@app.get('/get/imdb_score/{movie_name}/')

def get_imdb_score(movie_name:str):
    with open('imdb_movies.json',mode='r') as f:
        _data=json.load(f)
    for _rec in _data:
        if _rec['name'].lower()==movie_name.lower():
            return ({'movie_name':movie_name,
                                      'imdb_score':_rec['imdb_score']
                                      }
                
            )
            
if __name__=='__main__':
    app.run()