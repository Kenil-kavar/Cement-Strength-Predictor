import requests

url = "http://127.0.0.1:8080/predict"
file_path = 'path_to_your_file.csv'  # Replace with the actual path to your CSV file
files = {'file': open(file_path, 'rb')}
response = requests.post(url, files=files)

print(response.text)
