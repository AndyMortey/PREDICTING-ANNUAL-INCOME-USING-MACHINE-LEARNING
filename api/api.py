from fastapi import FastAPI
import joblib
from pydantic import BaseModel
import pandas as pd


app = FastAPI()

class IncomeRequest(BaseModel):
    age: int 
    gender: object
    education: object
    marital_status: object
    race: object
    employment_type: object
    wage_per_hour: int
    working_week_per_year: int
    industry: object
    capital_gain: int
    capital_losses: int
    citizenship: object
    country_of_birth: object

@app.get('/')
def status_check():
    return {"Status": "API is Online..."}

# Load models and encoder
gradient_boost = joblib.load('gradient_boost_pipeline.pkl')
random_forest = joblib.load('random_forest_pipeline.pkl')
encoder = joblib.load('label_encoder.pkl')

@app.post('/predict')
def predict_income(data: IncomeRequest):
    # Convert input data to DataFrame
    df = pd.DataFrame([data.dict()])

    # Make predictions
    prediction_grad = gradient_boost.predict(df)[0]
    prediction_ran = random_forest.predict(df)[0]
    
    # Get prediction probabilities
    prob_grad = gradient_boost.predict_proba(df)[0]
    prob_ran = random_forest.predict_proba(df)[0]
    
    # Convert predictions to int
    prediction_log = int(prediction_grad)
    prediction_ran = int(prediction_ran)
    
    # Inverse transform predictions
    prediction_grad = encoder.inverse_transform([prediction_grad])[0]
    prediction_ran = encoder.inverse_transform([prediction_ran])[0]

    return {
        "gradient_boost_prediction": prediction_grad,
        "random_forest_prediction": prediction_ran,
        "gradient_boost_probability": prob_grad.tolist(),
        "random_forest_probability": prob_ran.tolist()
    }
