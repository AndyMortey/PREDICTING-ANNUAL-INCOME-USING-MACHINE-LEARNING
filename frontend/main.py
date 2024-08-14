import streamlit as st
import requests
import pandas as pd
import sqlite3
from datetime import datetime

# Define the URL of your FastAPI service
FASTAPI_URL = "https://predicting-annual-income-using-machine.onrender.com/docs"

# Set up SQLite database connection
conn = sqlite3.connect('predictions.db')
c = conn.cursor()
c.execute('''
    CREATE TABLE IF NOT EXISTS predictions (
        timestamp TEXT,
        age INTEGER,
        wage_per_hour REAL,
        working_week_per_year INTEGER,
        capital_gain REAL,
        capital_losses REAL,
        gender TEXT,
        education TEXT,
        marital_status TEXT,
        race TEXT,
        employment_type TEXT,
        industry TEXT,
        citizenship TEXT,
        country_of_birth TEXT,
        income_level TEXT
    )
''')
conn.commit()

# Function to get the prediction from the FastAPI service
def get_prediction(data):
    try:
        response = requests.post(FASTAPI_URL, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error: {e}")
        return None

# Function to save prediction to SQLite database
def save_prediction(data, income_level):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with conn:
        c.execute('''
            INSERT INTO predictions (timestamp, age, wage_per_hour, working_week_per_year, capital_gain, 
                                      capital_losses, gender, education, marital_status, race, employment_type, 
                                      industry, citizenship, country_of_birth, income_level)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (timestamp, data['age'], data['wage_per_hour'], data['working_week_per_year'], data['capital_gain'],
              data['capital_losses'], data['gender'], data['education'], data['marital_status'], data['race'],
              data['employment_type'], data['industry'], data['citizenship'], data['country_of_birth'], income_level))

# Home Page
def home_page():
    st.title("Income Predictor")
    st.write("""
    Welcome to the Income Predictor app. This app uses a machine learning model to predict whether an individual's income is above or below a certain limit based on various features.
    """)
    st.image("frontend/Income_Page.png")

# Predict Page
def predict_page():
    st.title("Predict Income Level")
    
    # Input fields for user data
    age = st.number_input("Age", min_value=0, max_value=120, value=30)
    wage_per_hour = st.number_input("Wage per Hour", min_value=0.0, value=20.0)
    working_week_per_year = st.number_input("Working Weeks per Year", min_value=0, max_value=52, value=40)
    capital_gain = st.number_input("Capital Gain", min_value=0.0, value=0.0)
    capital_losses = st.number_input("Capital Losses", min_value=0.0, value=0.0)
    
    gender = st.selectbox("Gender", ["Male", "Female"])
    
    education_values = ['High_sch_grad', '12th_grade', 'Children', 'Bachelors', '7-8th-grade', 
                        '11th grade', '9th grade', 'Masters', '10th grade', 'Assoc-deg-aca',
                        '1st-2nd-3rd-4th grad', 'Some_college', 'Less than 1st grade',
                        'Assoc-deg-occup-voca', 'Professional_deg', '5th-6th grade', 'Doctorate']
    education = st.selectbox("Education", education_values)
    
    marital_status_values = ['Widowed', 'Never married', 'Married-Civilian-Spouse-Present', 'Divorced',
                             'Married-Spouse-Absent', 'Separated', 'Married-Armed-Force-Spouse-Present']
    marital_status = st.selectbox("Marital Status", marital_status_values)
    
    race_values = ['White', 'Black', 'Asian-Pacific-Islander', 'Amer-Indian-Eskimo', 'Other']
    race = st.selectbox("Race", race_values)
    
    employment_type = st.selectbox("Employment Type", ["Not in labor force", "Children/Armed Forces", "Full time", "Part time", "Unemployed"])
    
    industry_values = ['Unborn/Children', 'Hospital services', 'Retail trade',
                       'Finance insurance and real estate', 'Manufacturing-nondurable goods',
                       'Transportation', 'Business and repair services', 'Medical except hospital',
                       'Education', 'Construction', 'Manufacturing-durable goods',
                       'Public administration', 'Agriculture', 'Other professional services',
                       'Mining', 'Utilities and sanitary services', 'Private household services',
                       'Personal services except private HH', 'Wholesale trade', 'Communications',
                       'Entertainment', 'Social services', 'Forestry and fisheries', 'Armed Forces']
    industry = st.selectbox("Industry", industry_values)
    
    citizenship_values = ['Native', 'Non-Citizen', 'US citizen by naturalization',
                          'Native- Born abroad', 'Native- Born in Puerto Rico/US Outlying']
    citizenship = st.selectbox("Citizenship", citizenship_values)

    country_of_birth_values = ['US', 'Unknown', 'El-Salvador', 'Mexico', 'Philippines', 'Cambodia',
       'China', 'Hungary', 'Puerto-Rico', 'England', 'Dominican-Republic',
       'Japan', 'Canada', 'Ecuador', 'Italy', 'Cuba', 'Peru', 'Taiwan',
       'South Korea', 'Poland', 'Nicaragua', 'Germany', 'Guatemala',
       'India', 'Ireland', 'Honduras', 'France', 'Trinadad&Tobago',
       'Thailand', 'Iran', 'Vietnam', 'Portugal', 'Laos', 'Panama',
       'Scotland', 'Columbia', 'Jamaica', 'Greece', 'Haiti', 'Yugoslavia',
       'Outlying-U S (Guam USVI etc)', 'Holand-Netherlands', 'Hong Kong']
    country_of_birth = st.selectbox("Country of Birth", country_of_birth_values)
    
    # When the user clicks the Predict button
    if st.button("Predict"):
        # Prepare the data for prediction
        data = {
            "age": age,
            "wage_per_hour": wage_per_hour,
            "working_week_per_year": working_week_per_year,
            "capital_gain": capital_gain,
            "capital_losses": capital_losses,
            "gender": gender,
            "education": education,
            "marital_status": marital_status,
            "race": race,
            "employment_type": employment_type,
            "industry": industry,
            "citizenship": citizenship,
            "country_of_birth": country_of_birth
        }
        
        # Get the prediction
        prediction = get_prediction(data)
        
        if prediction:
            income_level = prediction.get("income_level", "Unknown")
            st.success(f"The predicted income level is: {income_level}")
            
            # Save the prediction to the database
            save_prediction(data, income_level)

# History Page
def history_page():
    st.title("Prediction History")
    
    # Query the database for predictions
    c.execute("SELECT * FROM predictions")
    rows = c.fetchall()
    
    if rows:
        df = pd.DataFrame(rows, columns=['Timestamp', 'Age', 'Wage per Hour', 'Working Weeks per Year', 'Capital Gain', 
                                         'Capital Losses', 'Gender', 'Education', 'Marital Status', 'Race', 
                                         'Employment Type', 'Industry', 'Citizenship', 'Country of Birth', 'Income Level'])
        st.dataframe(df)
    else:
        st.write("No predictions found.")

def data_page():
    st.title("Dataset Viewer")
    
    # Load dataset
    df = pd.read_csv('frontend/cleaned_dataset.csv')
    
    st.write("Here's a preview of the loaded dataset:")
    st.dataframe(df)

    uploaded_file = st.file_uploader("Choose a file")
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file)
        except UnicodeDecodeError:
            try:
                data = pd.read_csv(uploaded_file, encoding='latin1')
            except UnicodeDecodeError:
                st.error("The file could not be read with UTF-8 or latin1 encoding. Please check the file encoding.")
                return
        
        st.write("Here's a preview of your uploaded dataset:")
        st.dataframe(data)


# Sidebar navigation
st.sidebar.title("Navigation")
page = st.sidebar.radio("Go to", ["Home", "Data", "Predict", "History"])

# Show the selected page
if page == "Home":
    home_page()
elif page == "Data":
    data_page()
elif page == "Predict":
    predict_page()
elif page == "History":
    history_page()
