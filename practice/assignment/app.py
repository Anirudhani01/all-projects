from flask import Flask, render_template
import pandas as pd

app = Flask(__name__)

@app.route('/')
def show_employees():
    df = pd.read_csv('employees.csv')  # Load the CSV
    data = df.to_dict(orient='records')  # Convert to list of dicts for easy rendering
    return render_template('index.html', employees=data)

if __name__ == '__main__':
    app.run(debug=True)
