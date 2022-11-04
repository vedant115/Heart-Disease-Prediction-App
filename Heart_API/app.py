from ast import Str
from flask import Flask, render_template, url_for, flash, redirect
import joblib
from flask import request
import datetime 
import mysql.connector
import numpy as np
import smtplib
from email.message import EmailMessage
# import urllib.request
# import urllib.parse
import os
from twilio.rest import Client


app = Flask(__name__, template_folder='templates')

dt = datetime.datetime.now()

try:
    conn = mysql.connector.connect(host="localhost", user="root", password="", database="heart")
    cursor=conn.cursor()
except:
    print("An exception occured")

@app.route("/")

@app.route("/Heart")
def cancer():
    return render_template("heart.html")

def ValuePredictor(to_predict_list, size):
    to_predict = np.array(to_predict_list).reshape(1,size)
    if(size==7):
        loaded_model = joblib.load(r'D:\Engineering\TE II\AI\mini-project\Heart_API\heart_model.pkl')
        result = loaded_model.predict(to_predict)
    return result[0]

@app.route('/predict', methods = ["POST"])
def predict():
    if request.method == "POST":
        to_predict_list = request.form.to_dict()
        
        to_predict_list = list(to_predict_list.values())
        to_predict_list = list(map(str, to_predict_list))
        patientData = to_predict_list[:3]
        predictionData = to_predict_list[3:]
        predictionData = list(map(float, predictionData))

     #diabetes
    if(len(to_predict_list)==10):
        result = ValuePredictor(predictionData,7)
    
    if(int(result)==1):
        prediction = "You have chances of getting the Heart Disease. Please consult the doctor immediately!"
    else:
        prediction = "Don't fear. You don't have any symptoms of the disease."

    # Database Entry
    cursor.execute("""INSERT INTO `patients`(`name`, `mobno`, `email`, `chest_pain_type`, `resting_bp`, `cholestoral`, `fasting_blood_sugar`, `resting_electro-cardiographic_result`, `max_heart_rate`, `exercise_induced_angina`) VALUES ('{}','{}','{}','{}','{}','{}','{}','{}','{}','{}')""".format(patientData[0],patientData[1], patientData[2], predictionData[0], predictionData[1], predictionData[2], predictionData[3], predictionData[4], predictionData[5], predictionData[6],))
    conn.commit()

    # Email Sender
    msg = EmailMessage()
    txt = "Heart Disease Prediction APP : \nPatient's Name -" + patientData[0] + "\nChest Pain Type - " + str(predictionData[0]) + "\nResting Blood Pressure (in mm Hg) - " + str(predictionData[1]) + "\nSerum Cholestoral in mg/dl - " + str(predictionData[2]) + "\nFasting Blood Sugar - " + str(predictionData[3]) + "\nResting Electro-cardiographic Result - " + str(predictionData[4]) + "\nMaximum Heart Rate Achieved - " + str(predictionData[5]) + "\nExercise Induced Angina - " + str(predictionData[6]) + "\n\n" + prediction
    msg.set_content(txt)
    msg['subject'] = "Heart Disease Prediction Report"
    msg['to'] = patientData[2]

    user = "cloudprac826@gmail.com"
    msg['from'] = user
    password = "yrpiivywviauzyui"

    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.starttls()
    server.login(user, password)
    server.send_message(msg)

    server.quit()

    # SMS Sender
    account_sid = os.environ['TWILIO_ACCOUNT_SID'] = 'ACfb5600a0741045e414b1f8eb887de1f1'
    auth_token = os.environ['TWILIO_AUTH_TOKEN'] = 'c461338eb4c2b08540c4b672c93498a0'
    client = Client(account_sid, auth_token)

    message = client.messages.create(
                                body=txt,
                                from_='+19705333061',
                                to='+91' + patientData[1]
                            )

    print(message.sid)

    return(render_template("result.html", prediction_text=prediction))       

if __name__ == "__main__":
    app.run(debug=True)
