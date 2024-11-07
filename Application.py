from flask import Flask, request, jsonify
from model import ElectricityDemandForecast
import json

app = Flask(__name__)

demand_forecast = ElectricityDemandForecast("DataSet.csv")
demand_forecast.preprocess_data()
demand_forecast.train_model()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    start_datetime = f"{data['start_date']} {data['start_time']}"
    end_datetime = f"{data['end_date']} {data['end_time']}"

    try:
        result_df = demand_forecast.get_Value(start_datetime, end_datetime)
        result_json = result_df.to_json(orient='records')
        return jsonify({"result": result_json}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True)
