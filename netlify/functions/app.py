from flask import Flask, render_template, request, jsonify
import pandas as pd
import logging

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

app = Flask(__name__)

# Load the datasets with error handling
try:
    conversation_df = pd.read_csv('conversationo.csv')
    food_df = pd.read_csv('food.csv')
    item_to_id_df = pd.read_csv('item_to_id.csv')
    logging.info("CSV files loaded successfully")
except Exception as e:
    logging.error(f"Error loading CSV files: {e}")
    exit(1)  # Exit the application if there is an error

# Create a dictionary for quick lookup of responses
conversation_dict = dict(zip(conversation_df['Question'].str.lower().str.strip(), 
                              conversation_df['Answer'].str.strip()))

# Function to get response based on user input
def get_response(user_input):
    user_input = user_input.lower().strip()  # Normalize user input
    logging.debug(f"User input: {user_input}")  # Log the user input
    response = conversation_dict.get(user_input, "I'm sorry, I don't understand that.")
    
    # Check for food-related queries
    if "food" in user_input or "menu" in user_input:
        food_items = item_to_id_df['name'].tolist()
        if food_items:
            response += "\nHere are some items we have: " + ", ".join(food_items[:5])  # Show first 5 items
            logging.debug(f"Food items provided: {', '.join(food_items[:5])}")
        else:
            response += "\nSorry, I couldn't retrieve the food items at the moment."
            logging.warning("No food items retrieved")
    
    return response

@app.route('/')
def home():
    logging.info("Home route accessed")
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    try:
        user_input = request.form['user_input']
        logging.info(f"Received user input: {user_input}")  # Log received input
        
        response = get_response(user_input)
        
        logging.info(f"Response: {response}")  # Log the response
        return jsonify({'response': response})
    
    except Exception as e:
        logging.error(f"Error processing request: {e}")  # Log any errors
        return jsonify({'response': "Sorry, there was an error processing your request."})

# Serverless-wsgi integration to handle the Flask app
from serverless_wsgi import handle_request

def handler(event, context):
    logging.info("Serverless handler invoked")
    return handle_request(app, event, context)

if __name__ == "__main__":
    app.run(debug=True)  # Run the Flask app locally for debugging

