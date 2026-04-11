from flask import Flask, request, render_template

app = Flask(__name__)

def is_armstrong(number):
    num_str = str(number)
    power = len(num_str)
    total = sum(int(digit) ** power for digit in num_str)
    return total == number

@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    if request.method == "POST":
        num = request.form.get("number")
        if num and num.isdigit():
            number = int(num)
            result = f"{number} is an Armstrong number!" if is_armstrong(number) else f"{number} is not an Armstrong number."
        else:
            result = "Please enter a valid positive integer."
    return render_template("index.html", result=result)

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=5000)
