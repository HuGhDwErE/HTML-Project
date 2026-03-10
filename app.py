from flask import Flask, render_template, request

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("Html_project.html")

if __name__ =="__main__":
    app.run(debug=True)