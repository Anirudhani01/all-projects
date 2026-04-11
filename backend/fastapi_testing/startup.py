from fastapi import FastAPI
from pydantic import BaseModel,EmailStr


app=FastAPI()

class User(BaseModel):
    id:int
    name:str
    email:EmailStr
    company:str
    
@app.post('/user/')
def get_user(user:User):
    # _user=User()
    return{"id":user.id,
           "name":user.name,
           "email":user.email,
           "company":user.company
           }
    
    
if __name__=='__main__':
    app.run(host='127.0.0.1',port=8000,debug=True)