from flask import Flask, render_template, jsonify, request, send_file
from src.exception import CustomException
from src.logger import logging as lg
import os
import sys,json

from src.pipeline.train_pipeline import TrainPipeline
from src.pipeline.predict_pipeline import PredictionPipeline

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/train")
def train_route():
    try:
        train_pipeline = TrainPipeline()
        train_pipeline.run_pipeline()

        return jsonify(message="Training Successful.")
    except Exception as e:
        lg.error(f"Error during training: {str(e)}")
        return jsonify(error=str(e)), 500

@app.route("/predict", methods=['POST', 'GET'])
def predict():
    try:
        if request.method == "POST":
            if not request.form:
                return jsonify({"error": "No form data in the request"}), 400
#  Cement (component 1)(kg in a m^3 mixture),
# Blast Furnace Slag (component 2)(kg in a m^3 mixture),
# Fly Ash (component 3)(kg in a m^3 mixture),
# Water  (component 4)(kg in a m^3 mixture),
# Superplasticizer (component 5)(kg in a m^3 mixture),
# Coarse Aggregate  (component 6)(kg in a m^3 mixture),
# Fine Aggregate (component 7)(kg in a m^3 mixture),
# Age (day),
# "Concrete compressive strength(MPa, megapascals) "           
            Cement_component=int(request.form.get("cement"))
            Blast = float(request.form.get('blast_furnace_slag'))
            Fly= float(request.form.get('fly_ash'))
            Water= float(request.form.get('water'))
            Superplasticizer= float(request.form.get('superplasticizer'))
            Coarse = float(request.form.get('coarse_aggregate'))
            Fine = float(request.form.get('fine_aggregate'))
            Age = float(request.form.get('age'))
            
            
            # Extract form data
            #data = dict(request.form)
            #lg.info(f"Form data received: {data}")
            data = {
                "Cement (component 1)(kg in a m^3 mixture)": Cement_component,
                "Blast Furnace Slag (component 2)(kg in a m^3 mixture)": Blast,
                "Fly Ash (component 3)(kg in a m^3 mixture)": Fly,
                "Water  (component 4)(kg in a m^3 mixture)": Water,
                "Superplasticizer (component 5)(kg in a m^3 mixture)": Superplasticizer,
                "Coarse Aggregate  (component 6)(kg in a m^3 mixture)": Coarse,
                "Fine Aggregate (component 7)(kg in a m^3 mixture)": Fine,
                "Age (day)": Age
            
            }
            prediction_pipeline = PredictionPipeline(data)
            prediction_file_detail = prediction_pipeline.run_pipeline()

            lg.info("Prediction completed. Downloading prediction file.")
            return send_file(prediction_file_detail.prediction_file_path,
                             download_name=prediction_file_detail.prediction_file_name,
                             as_attachment=True)

    except Exception as e:
        raise CustomException(e, sys)

    return jsonify({"error": "Invalid request"}), 400  # For example, return a simple error response

@app.route('/upload', methods=['POST', 'GET'])
def upload():
    try:
        if request.method == 'POST':
            prediction_pipeline = PredictionPipeline(request)
            prediction_file_detail = prediction_pipeline.run_pipeline()

            lg.info("Prediction completed. Downloading prediction file.")
            return send_file(prediction_file_detail.prediction_file_path,
                             download_name=prediction_file_detail.prediction_file_name,
                             as_attachment=True)
        else:
            return render_template('upload_file.html')
    except Exception as e:
        lg.error(f"Error during file upload: {str(e)}")
        return jsonify(error=str(e)), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
