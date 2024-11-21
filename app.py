import matplotlib
import ollama
import pandas as pd
import matplotlib.pyplot as plt
import io
from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore
from vanna.flask import VannaFlaskApp
from flask import Flask, request, jsonify, Response, send_file, send_from_directory
from pyngrok import ngrok
from tabulate import tabulate
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
app = Flask(__name__,static_folder="static")
matplotlib.use("Agg")
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
    vn.connect_to_mysql(host='172.21.11.46', dbname='payu_hack', user='root', password='P@55phrase', port=3306)

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
        logging.info(dataframe)
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
def create_table_image(dataframe):
    # Create a matplotlib figure
    fig, ax = plt.subplots(figsize=(6, len(dataframe) * 0.6))  # Adjust size based on rows
    ax.axis("off")  # Hide axes

    # Create the table
    table = plt.table(
        cellText=dataframe.values,
        colLabels=dataframe.columns,
        cellLoc="center",
        loc="center",
    )

    # Style adjustments
    table.auto_set_font_size(False)
    table.set_fontsize(12)
    table.auto_set_column_width(col=list(range(len(dataframe.columns))))

    # Save the image to a BytesIO buffer
    buffer = io.BytesIO()
    plt.savefig(buffer, format="png", bbox_inches="tight")
    buffer.seek(0)
    plt.close(fig)  # Close the plot
    return buffer

def create_bar_graph(df):
    
    values = [73.5, 8.0, 12.3, 15.7]

    # Create the bar graph
    plt.figure(figsize=(8, 6))  # Adjust the figure size
    modes = df['mode'].tolist()
    srts = df['SRT'].tolist()
    plt.bar(modes, srts, color='skyblue')

    # Add labels and title
    plt.title('Payment Options and SRT', fontsize=16)
    plt.xlabel('Payment Options', fontsize=14)
    plt.ylabel('SRT', fontsize=14)

    # Show the graph
    plt.grid(axis='y', linestyle='--', alpha=0.7)
    plt.savefig('static/table_image.png', dpi=300, bbox_inches='tight')
    plt.show()

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

@app.route('/static/<path:filename>')
def static_files(filename):
    return send_from_directory(app.static_folder, filename)

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
                return jsonify({'error': 'Invalid input'}), 401
        
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
    
# API endpoint
@app.route('/onboard', methods=['POST'])
def onboard():
    try:
        data = request.get_json()
        logging.info(f"chat req: {data}")
        if not data :
            if 'input' not in data:
                logging.warning("Invalid request payload")
                return jsonify({'error': 'Invalid input'}), 400
        
        prompt = data['prompt']
        logging.info(f"Received input: {prompt}")
 # Connect to the MySQL database
        connection = mysql.connector.connect(
            host=db_config["host"],
            user=db_config["user"],
            password=db_config["password"],
            database=db_config["database"]
        )
        cursor = connection.cursor(dictionary=True)

      
        # Call internal function
        if prompt=="Payment Modes & SRT":
            # Query the database
            query = """
            SELECT mode,last_1_month as SRT FROM aggregated_mode_srt_gmv
            WHERE type='SRT' and merchantid=0
            """
            cursor.execute(query)
            result = cursor.fetchall()
            df = pd.DataFrame(result)
            logging.info(f"mode&srt: {df.to_json(orient='records', indent=2)}")
            table_string = tabulate(df, headers="keys", tablefmt="grid",showindex=False)
            description = "Below are payment options and PayU SRT:\n"
            response_string = description + table_string
            response_string = response_string + "For visualization you can visit below link:"
            # image_buffer = create_table_image(df)
            image_path = "static/table_image.png"  # Save locally
            # with open(image_path, "wb") as f:
            #     f.write(image_buffer.getvalue())
            create_bar_graph(df)

    # Respond with JSON containing the summary key
            response = {
                "summary": response_string + f"https://3cee-14-143-127-46.ngrok-free.app//{image_path}"
            }
            return jsonify(response)
            # response_summary = summarize_dataframe(prompt,df)
            # return jsonify({"summary":response_string}), 200
        # logging.info(f"Returning response: {response}")
        else:
            return jsonify({'summary': 'Sorry for inconvenience, We are not able to find your query'}),400
        
        

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return jsonify({'error': 'Internal Server Error'}), 500


if __name__ == '__main__':
    initLLM()
    app.run(host="127.0.0.1",port=5000)
