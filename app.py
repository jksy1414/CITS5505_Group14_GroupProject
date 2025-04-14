from flask import Flask, render_template

app = Flask(__name__)

# Route for input page
@app.route('/analyze')
def analyze():
    return render_template('input_analyze.html')

# Route for output page
@app.route('/results')
def results():
    return render_template('output_result.html')

if __name__ == '__main__':
    app.run(debug=True)
