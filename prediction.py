import pandas as pd
import joblib

def predict_failure(data):
    df_year_failure = pd.DataFrame(data)
    one_class_svm_model = joblib.load('trained model/one_class_svm_model.pkl')
    x_year = df_year_failure
    anomaly_predictions_year = one_class_svm_model.predict(x_year)
    result_df = pd.DataFrame({'predicted_failure': anomaly_predictions_year})
    result_df['predicted_failure'] = result_df['predicted_failure'].apply(lambda x: 'not critical' if x == 1 else 'critical')
    return result_df