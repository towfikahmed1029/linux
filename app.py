from flask import Flask, render_template, request, redirect, url_for, flash
import requests
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)


def Zestimate(address):
    # return 5
    url = "https://zillow-api19.p.rapidapi.com/"
    querystring = {"address":address}
    # querystring = {"address":"12364 Saint Bernard Dr, Truckee, CA 96161"}

    headers = {
        "x-rapidapi-key": "0936e447c1msh9180e3d2b9d0c34p1eee57jsn1dfc603daa38",
        "x-rapidapi-host": "zillow-api19.p.rapidapi.com"
    }

    response = requests.get(url, headers=headers, params=querystring)
    return response.json().get("zestimate")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/submit', methods=['POST'])
def submit():
    error_message = None
    name = request.form['name']
    phone = request.form['phone']
    email = request.form['email']
    address =request.form['address']
    Average_Construction= request.form['Average_Construction']
    Sqft = request.form['Sqft']
    Level_of_Damage = request.form['Level_of_Damage']
    
    try:
        Level_of_Damage = int(Level_of_Damage)
    except:
        error_message = 'Invalid Level of Damage!'
    try:
        Sqft = float(Sqft)
    except:
        error_message = 'Invalid Sqft!'
    try:
        Average_Construction = float(Average_Construction)
    except:
        error_message ='Invalid Average Construction!'
    try:
        Average_Construction = float(Average_Construction)
    except:
        error_message ='Invalid Average Construction!'
    if not valid_email(email):
        error_message = 'Invalid email address!'
    if not phone.isdigit() or len(phone) < 10:
        error_message = 'Invalid phone number!'

    if error_message:
        return render_template('index.html', error_message=error_message)
    
    Zestimate_address = Zestimate(address)
    
    operation1 = Sqft * Average_Construction
    operation2 =  (Zestimate_address) * 0.40 
    operation3 = operation2 - operation1
    
    # = Offer = Offer Range (+ or - $50,000)

    return render_template('result.html', name=name, email=email,phone=phone,Formula=operation3)


if __name__ == '__main__':
    app.run()
    # app.run(debug=True)
