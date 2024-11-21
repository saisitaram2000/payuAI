import ollama
import pandas as pd
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from flask import Flask, request, jsonify
from pyngrok import ngrok
import logging
import mysql.connector
import asyncio

# session = boto3.Session()
# boto3_bedrock = boto3.client(service_name="bedrock-runtime")

class PayuAiInit(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

#app and logging initialization
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
vn = None
db_config = {
    "host": "172.21.11.46",
    "user": "root",
    "password": "P@55phrase",
    "database": "payu_hack"
}

def initLLM():
    global vn
    vn = PayuAiInit(config={'model': 'mistral'})
    vn.connect_to_mysql(host='172.21.11.46', dbname='payu', user='root', password='P@55phrase', port=3306)

async def preload_context(merchant_data):
    try:
        # Simulate context preloading (e.g., fetching related data)
        await asyncio.sleep(1)  # Simulate async processing
        print(f"Preloading context for merchant: {merchant_data}")
        # Add actual preloading logic here
    except Exception as e:
        print(f"Error during context preloading: {str(e)}")
    
# print(training_data)
# print(val)
# print(df)
# app = VannaFlaskApp(vn)
# app.run()
def summarize_dataframe(prompt, dataframe):
    """
    Generate a text summary of a DataFrame using Ollama.
    """
    try:
        # Convert DataFrame to JSON
        json_data = dataframe.to_json(orient='records', indent=2)
        logging.info(f"DataFrame converted to JSON: {json_data}")

        # Create a prompt for the LLM
        prompt = (
            f"You are an AI assistant. A merchant has asked the following question:\n\n"
            f"'{prompt}'\n\n"
            f"Based on the following data, summarize the results into a concise, meaningful text:\n"
            f"{json_data}"
        )

        response = ollama.chat(model='mistral', messages=[
        {
            'role': 'user',
            'content': prompt,
        },
        ])

        # Call the LLM to generate the summary
        summary = response['message']['content']
        logging.info(f"Generated summary: {summary}")

        return summary
    except Exception as e:
        logging.error(f"Error summarizing DataFrame: {e}")
        raise

# Internal function
def process_input(prompt,merchantId):
    global vn
    logging.info(f"Processing input: {prompt} for MID: {merchantId}")
    # Example processing: Reverse the input string
    # response = user_input[::-1]
    # sql = vn.generate_sql("find SRT of merchant 180012 for debitcard for last 1 week")
    sql_query = vn.generate_sql(f"{prompt} for merchant {merchantId}")
    logging.info(f"Executing SQL query : {sql_query} ")
    responseDf = vn.run_sql(sql_query)
    response_summary = summarize_dataframe(prompt,responseDf)
    logging.info(f"Processed response: {response_summary}")
    return response_summary

# API endpoint
@app.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.get_json()
        logging.info(f"chat req: {data}")
        if not data :
            if 'input' not in data:
                logging.warning("Invalid request payload")
                return jsonify({'error': 'Invalid input'}), 400
            elif 'merchantId' not in data:
                logging.warning("merchantId not present")
                return jsonify({'error': 'Invalid input'}), 400
        
        prompt = data['prompt']
        merchantId = data['merchantid']
        logging.info(f"Received input: {prompt}")

        # Call internal function
        response = process_input(prompt,merchantId)

        logging.info(f"Returning response: {response}")
        return jsonify({'summary': response}), 200

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500
    
@app.route('/authenticate', methods=['POST'])
def validate_merchant():
    try:
        # Parse the input JSON
        global db_config
        data = request.json
        phone = data.get("phone")
        merchant_id = data.get("merchantid")
        logging.info(f"data: {data}")
        if not phone or not merchant_id:
            return jsonify({"error": "Missing phone or merchantid"}), 400

        # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        cursor = connection.cursor(dictionary=True)

        # Query the database
        query = """
        SELECT * FROM merchant
        WHERE id = %s AND phone = %s
        """
        cursor.execute(query, (merchant_id, phone))
        result = cursor.fetchone()

        # Close the database connection
        cursor.close()
        connection.close()

        # Check if the result exists
        if result:
            asyncio.run(preload_context(result))
            return jsonify({"message": "Merchant validated"}), 200
        else:
            return jsonify({"error": "Merchant not found or phone mismatch"}), 401

    except mysql.connector.Error as e:
        return jsonify({"error": f"Database error: {str(e)}"}), 500
    except Exception as e:
        return jsonify({"error": f"An unexpected error occurred: {str(e)}"}), 500


if __name__ == '__main__':
    initLLM()
    app.run(host="127.0.0.1",port=5000)
