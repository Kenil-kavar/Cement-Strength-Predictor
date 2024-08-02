import shutil
import os
import sys
import pandas as pd
from src.logger import logging
from src.exception import CustomException
from flask import request
from src.utils import load_object
from dataclasses import dataclass
import json

@dataclass
class PredictionFileDetail:
    prediction_output_dirname: str = "predictions"
    prediction_file_name: str = "predicted_file.csv"
    prediction_file_path: str = os.path.join(prediction_output_dirname, prediction_file_name)

class PredictionPipeline:
    def __init__(self, request_data):
        self.request_data = request_data
        
        self.prediction_file_detail = PredictionFileDetail()

    def save_input_file(self, data):  # Added 'self' parameter
        try:
            input_dir = "input_files"
            file_name = "file.json"  # Consider adding a file extension
            if not os.path.exists(input_dir):
                os.makedirs(input_dir)

            file_path = os.path.join(input_dir, file_name)

            with open(file_path, 'w') as file:
                json.dump(data, file, indent=4)

            return file_path
        except Exception as e:
            logging.error(f"Error in save_input_file: {e}")
            raise CustomException(e, sys)



    def get_prediction(self, features: pd.DataFrame) -> pd.DataFrame:
        try:
            model = load_object(file_path="artifacts/model.pkl")
            predictions = model.predict(features)
            features["predictions"] = predictions
            return features
        except Exception as e:
            raise CustomException(e, sys)


    def get_extracted_data(self, input_file_path: str) -> pd.DataFrame:
        try:
            with open(input_file_path, 'r') as file:
                data1 = json.load(file)
            print("JSON data:", data1)
            train = pd.DataFrame(data1,index=['row_index'])
            return train
        except Exception as e:
            raise CustomException(e, sys)


    def initiate_prediction(self, input_file_path):
        try:
            df = self.get_extracted_data(input_file_path=input_file_path)
            prediction = self.get_prediction(df)
            return prediction
        except Exception as e:
            raise CustomException(e, sys)

    def save_prediction(self, prediction: pd.DataFrame):
        try:
            os.makedirs(self.prediction_file_detail.prediction_output_dirname, exist_ok=True)
            prediction.to_csv(self.prediction_file_detail.prediction_file_path, index=False, header=True)
        except Exception as e:
            raise CustomException(e, sys)

    def run_pipeline(self) -> PredictionFileDetail:
        try:
            input_file_path = self.save_input_file(self.request_data)
            prediction = self.initiate_prediction(input_file_path=input_file_path)
            self.save_prediction(prediction=prediction)
            logging.info("Removing input file from directory")
            os.remove(input_file_path)
            return self.prediction_file_detail
        except Exception as e:
            raise CustomException(e, sys)