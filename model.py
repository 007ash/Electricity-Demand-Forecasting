import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from sklearn.model_selection import TimeSeriesSplit
import xgboost as xgb
from sklearn.metrics import mean_squared_error
import os

import warnings
warnings.filterwarnings("ignore")

class ElectricityDemandForecast:

    def __init__(self, file_path, model_file='model.json'):

        self.df = pd.read_csv(file_path)
        self.model_file = model_file 
        self.model = None
        self.future_w_features = None
        self.scores = []

        if os.path.exists(self.model_file):
            self.load_model(self.model_file)
        else:
            self.model = None

    def preprocess_data(self):

        self.df = self.df.rename(columns={'date': 'Date', 'hour': 'Hour'})
        self.df['Hour'] = self.df['Hour'].astype(str).str.zfill(2)
        self.df['Hour'] = pd.to_numeric(self.df['Hour'], errors='coerce')

        def convert_range(value):

            if value == '01':
                return 0
            elif value > 24:
                raise ValueError("Value exceeds 24")
            else:
                return int(value) - 1 if isinstance(value, int) else int(value[1:])

        self.df['Hour'] = self.df['Hour'].apply(convert_range)
        self.df['Hour'] = self.df['Hour'].apply(lambda x: f"{x:02d}")
        self.df['Hour'] = self.df['Hour'].astype(str) + ':00:00'

        self.df["DateTime"] = self.df[["Date", "Hour"]].apply(" ".join, axis=1)
        self.df["DateTime"] = pd.to_datetime(self.df["DateTime"], dayfirst=True)
        self.df = self.df[['DateTime', 'hourly_demand']].set_index('DateTime').sort_index()

    def create_features(self, df):

        df = df.copy()
        df['hour'] = df.index.hour
        df['dayofweek'] = df.index.dayofweek
        df['quarter'] = df.index.quarter
        df['month'] = df.index.month
        df['year'] = df.index.year
        df['dayofyear'] = df.index.dayofyear
        df['dayofmonth'] = df.index.day
        df['weekofyear'] = df.index.isocalendar().week
        return df

    def add_lags(self, df):

        target_map = df['hourly_demand'].to_dict()
        df['lag1'] = (df.index - pd.Timedelta('364 days')).map(target_map)
        df['lag2'] = (df.index - pd.Timedelta('728 days')).map(target_map)
        df['lag3'] = (df.index - pd.Timedelta('1092 days')).map(target_map)
        return df

    def train_model(self, n_splits=5, test_size=24 * 365, gap=24):

        tss = TimeSeriesSplit(n_splits=n_splits, test_size=test_size, gap=gap)
        fold = 0
        preds = []
        self.scores = []

        for train_idx, val_idx in tss.split(self.df):
            train = self.df.iloc[train_idx]
            test = self.df.iloc[val_idx]

            train = self.create_features(train)
            test = self.create_features(test)

            print(f"Train shape after creating features: {train.shape}")
            print(f"Test shape after creating features: {test.shape}")

            train = self.add_lags(train)
            test = self.add_lags(test)

            print(f"Train shape after adding lags: {train.shape}")
            print(f"Test shape after adding lags: {test.shape}")

            train = train.dropna()
            test = test.dropna()

            print(f"Train shape after dropping NaNs: {train.shape}")
            print(f"Test shape after dropping NaNs: {test.shape}")

            if len(train) == 0 or len(test) == 0:
                print(f"Fold {fold}: No data after dropping missing values.")
                continue  

            FEATURES = ['dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year', 'lag1', 'lag2', 'lag3']
            TARGET = 'hourly_demand'

            X_train = train[FEATURES]
            y_train = train[TARGET]

            X_test = test[FEATURES]
            y_test = test[TARGET]

            if X_train.empty or X_test.empty:
                print(f"Fold {fold}: No data for training or testing.")
                continue

            reg = xgb.XGBRegressor(base_score=0.5, booster='gbtree',
                                   n_estimators=1000,
                                   early_stopping_rounds=50,
                                   objective='reg:linear',
                                   max_depth=3,
                                   learning_rate=0.01)
            reg.fit(X_train, y_train, eval_set=[(X_train, y_train), (X_test, y_test)], verbose=100)

            y_pred = reg.predict(X_test)
            preds.append(y_pred)
            score = np.sqrt(mean_squared_error(y_test, y_pred))
            self.scores.append(score)

            fold += 1

        if len(self.scores) > 0:
            print(f'Score across folds {np.mean(self.scores):0.4f}')
            print(f'Fold scores: {self.scores}')
            self.model = reg  
        else:
            print("No folds completed successfully.")

    def forecast_future(self, start_date, end_date):

        future = pd.date_range(start_date, end_date, freq='1h')
        future_df = pd.DataFrame(index=future)
        future_df['isFuture'] = True
        self.df['isFuture'] = False
        df_and_future = pd.concat([self.df, future_df])

        df_and_future = self.create_features(df_and_future)
        df_and_future = self.add_lags(df_and_future)

        future_w_features = df_and_future.query('isFuture').copy()
        future_w_features['pred'] = self.model.predict(future_w_features[self.get_features()])

        future_w_features['pred'].plot(figsize=(20, 5), color='Green', title='Future Predictions')

        self.future_w_features = future_w_features

    def get_Value(self,start_date, end_date):

        future = pd.date_range(start_date, end_date, freq='1h')
        future_df = pd.DataFrame(index=future)
        future_df['isFuture'] = True
        self.df['isFuture'] = False
        df_and_future = pd.concat([self.df, future_df])

        df_and_future = self.create_features(df_and_future)
        df_and_future = self.add_lags(df_and_future)

        future_w_features = df_and_future.query('isFuture').copy()
        future_w_features['pred'] = self.model.predict(future_w_features[self.get_features()])


        return future_w_features[['month', 'year','hour','pred']]

    def save_model(self, file_name):

        if self.model:
            self.model.save_model(file_name)
            print(f"Model saved as {file_name}")

    def load_model(self, file_name):

        reg_new = xgb.XGBRegressor()
        reg_new.load_model(file_name)
        print(f"Model loaded from {file_name}")
        self.model = reg_new

    def get_features(self):

        return ['dayofyear', 'hour', 'dayofweek', 'quarter', 'month', 'year', 'lag1', 'lag2', 'lag3']

