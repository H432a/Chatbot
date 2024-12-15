from flask import Flask, render_template, request, jsonify
import pandas as pd

app = Flask(__name__)

# Load the datasets with error handling
try:
    conversation_df = pd.read_csv('conversationo.csv')
    food_df = pd.read_csv('food.csv')
    item_to_id_df = pd.read_csv('item_to_id.csv')
except Exception as e:
    print(f"Error loading CSV files: {e}")
    exit(1)  # Exit the application if there is an error

# Create a dictionary for quick lookup of responses
conversation_dict = dict(zip(conversation_df['Question'].str.lower().str.strip(), 
                              conversation_df['Answer'].str.strip()))

# Function to get response based on user input
def get_response(user_input):
    user_input = user_input.lower().strip()  # Normalize user input
    response = conversation_dict.get(user_input, "I'm sorry, I don't understand that.")

    # Check for food-related queries
    if "food" in user_input or "menu" in user_input:
        food_items = item_to_id_df['name'].tolist()
        if food_items:
            response += "\nHere are some items we have: " + ", ".join(food_items[:5])  # Show first 5 items
        else:
            response += "\nSorry, I couldn't retrieve the food items at the moment."

    return response

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    response = get_response(user_input)
    return jsonify({'response': response})

if __name__ == '__main__':
    app.run(debug=True)
