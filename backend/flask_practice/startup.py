from flask import Flask

app=Flask(__name__)

@app.route('/is_armstrong/<int:number>')

def is_armstrong(number):
    num_str = str(number)
    num_digits = len(num_str)
    total = sum(int(digit) ** num_digits for digit in num_str)
    return str(total == number)


    
if __name__ == '__main__':
    app.run(debug=True, host='127.0.0.1',port=5000)
