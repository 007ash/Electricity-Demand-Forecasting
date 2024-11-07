from model import ElectricityDemandForecast

if __name__ == "__main__":

    start = '2026-11-20 00:00:00'
    end = '2026-11-21 06:00:00'

    demand_forecast = ElectricityDemandForecast("DataSet.csv")
    demand_forecast.preprocess_data()
    demand_forecast.train_model()
    demand_forecast.forecast_future(start, end)
    print("-------------- Values -----------")
    print(demand_forecast.get_Value(start,end))

    demand_forecast.save_model('model.json')
    demand_forecast.load_model('model.json')