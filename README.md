# Electricity Demand Forecasting

This project predicts future electricity demand from historical hourly usage data using an XGBoost regression model. It includes a desktop UI built with Tkinter, a Flask API for web integration, and a simple browser frontend that can request predictions and plot them with Chart.js.

## Features

- Forecast hourly electricity demand for a selected date/time range.
- Train a time-series model on `DataSet.csv`.
- Use a desktop interface with date pickers and a demand chart.
- Expose predictions through a Flask `/predict` endpoint.
- Render results in a lightweight HTML/JavaScript frontend.

## Project Structure

- `model.py` - core data preprocessing, feature engineering, training, and forecasting logic.
- `app.py` - Tkinter desktop application.
- `Application.py` - Flask API backend.
- `test2.py` - example script that trains the model and saves it.
- `index.html`, `script.js`, `style.css` - browser frontend.
- `DataSet.csv` - training data used by the model.
- `Documents/` and `Output images/` - supporting documentation and screenshots.

## Requirements

Install Python 3.10+ and the following packages:

```bash
pip install pandas numpy matplotlib scikit-learn xgboost flask tkcalendar
```

`tkinter` is part of the standard Python distribution on most systems. If it is missing on Linux, install it through your package manager.

## Run the Desktop App

The Tkinter app loads the dataset, trains the model, and lets you request predictions from a start and end datetime.

```bash
python app.py
```

## Run the Flask API

Start the backend server:

```bash
python Application.py
```

The API exposes:

- `POST /predict`

Example request body:

```json
{
	"start_date": "2026-11-20",
	"start_time": "00:00",
	"end_date": "2026-11-21",
	"end_time": "06:00"
}
```

Example response:

```json
{
	"result": "[...]"
}
```

## Run the Browser Frontend

The HTML frontend calls the Flask API at `http://localhost:5000/predict`, so make sure the backend is running first.

Open `index.html` in a browser, enter a date range, and click Display Values.

## Sample Script

`test2.py` shows a minimal end-to-end flow:

1. Load `DataSet.csv`
2. Preprocess the data
3. Train the model
4. Generate a forecast
5. Save and reload the model as `model.json`

Run it with:

```bash
python test2.py
```

## How It Works

1. The dataset is normalized into a datetime index.
2. Calendar features such as hour, day of week, month, and year are created.
3. Lag features are added to capture demand patterns from previous years.
4. An XGBoost regressor is trained with time-series cross-validation.
5. Predictions are returned for the requested future time range.

## Notes

- The current implementation trains the model when the app starts.
- If you plan to reuse the model often, call `save_model()` after training and load the saved file later.
- The API and the desktop app both use the shared forecasting logic in `model.py`.

## License

No license file is included in the repository.
