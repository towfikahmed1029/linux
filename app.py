from flask import Flask, render_template, request, redirect, url_for, session, jsonify
# from langchain.agents import create_sql_agent
# from langchain.agents.agent_toolkits import SQLDatabaseToolkit
# from langchain.sql_database import SQLDatabase
from langchain_community.agent_toolkits.sql.base import create_sql_agent
from langchain_community.agent_toolkits.sql.toolkit import SQLDatabaseToolkit
from langchain_community.utilities import SQLDatabase

from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from langchain_openai import ChatOpenAI
from sqlalchemy import inspect
import os
import pyodbc
import datetime
import io
import sys

os.environ["OPENAI_API_KEY"] = "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"

private_key = 'a1'
# Replace the following variables with your own details
server = 'peakhuman.database.windows.net'
database = 'Lab Values'
username = 'peakhuman'
password = 'Toronto888#'
driver = '{ODBC Driver 18 for SQL Server}'

# # def db_connection():
conn_string = f'DRIVER={driver};SERVER=tcp:{server},1433;DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=120;'

try:
    conn = pyodbc.connect(conn_string)
    print("Connection successful")
    conn.close()
except pyodbc.Error as ex:
    print("Connection failed")
    print(ex)
    exit(1)  

connection_url = URL.create(
    "mssql+pyodbc",
    query={"odbc_connect": conn_string} )

llm = ChatOpenAI(model_name="gpt-3.5-turbo")
db_engine = create_engine(connection_url, pool_pre_ping=True, pool_recycle=3600)
db = SQLDatabase(db_engine)
sql_toolkit = SQLDatabaseToolkit(db=db, llm=llm)

agent_executor = create_sql_agent(
    llm=llm,
    toolkit=sql_toolkit,
    # verbose=True,
    handle_parsing_errors=True,
)
    # return agent_executor

# inspector = inspect(db_engine)
# TOPICS = table_names = inspector.get_table_names(schema='dbo')
TOPICS = ['oscarReport eGFR','oscarReport HDL','oscarReport Lipids LDL','oscarReport TCHOL','oscarReport LIPIDS TG','genome_Sanjeev_Goel',
'api_report_data','glycan_report_data','labReportAll','oscarReport AIC','oscarReport BF','oscarReport Hb','oscarReport Hb 2021-22',
'oscarReport Waist 2018-23','oscarReport LDL ','oscarReport WT ','oscarReport SMK','oscarReport TG','oscarReport BP',
'oscarReport AST','oscarReport creatinine',]

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

def log_write(user_message_f,ai_message,operation):
    current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    all_text = f"LangChain operations started at: {current_time}\n"
    all_text += f"Question: {user_message_f}\n"
    all_text += f"Output: {ai_message}\n"
    all_text += f"Operation: {operation}\n"
    
    file_name = 'log.txt'
    try:
        with open(file_name, 'r', encoding='utf-8') as file:
            current_content = file.read()
    except FileNotFoundError:current_content = ""
    entries = current_content.split("LangChain operations started at:")
    entries = [entry for entry in entries if entry.strip()]
    entries = ["LangChain operations started at:" + entry for entry in entries]
    new_entry = all_text + "\n"
    entries.insert(0, new_entry)
    entries = entries[:5]
    new_content = "".join(entries)
    with open(file_name, 'w', encoding='utf-8') as file:
        file.write(new_content)

# Route for the home page
@app.route('/', methods=['GET', 'POST'])
def index():
    
    if request.method == 'POST':
        if request.form['key'] == private_key:
            session['logged_in'] = True
            return redirect(url_for('index'))
        else:
            return render_template('login.html', error='Invalid private key')
    if not session.get('logged_in'):
        return render_template('login.html', error=None)
    return render_template('index.html', topics=TOPICS)

@app.route('/log', methods=['GET', 'POST'])
def log():
    if not session.get('logged_in'):
        return render_template('login.html', error=None)
    try:
        with open('log.txt', 'r', encoding='utf-8') as file:
            log_content = file.read()
    except FileNotFoundError:
        log_content = "Log file not found."
    entries = log_content.split("\n\n")
    return render_template('log.html', entries=entries)

@app.route('/logout', methods=['GET'])
def logout():
    session.clear()  # Clear all session data
    return redirect(url_for('index'))

@app.route('/log', methods=['GET', 'POST'])
def log():
    if not session.get('logged_in'):
        return render_template('login.html', error=None)
    try:
        with open('log.txt', 'r', encoding='utf-8') as file:
            log_content = file.read()
    except FileNotFoundError:
        log_content = "Log file not found."
    entries = log_content.split("\n\n")
    return render_template('log.html', entries=entries)

# Route to handle chat messages
@app.route('/send_message', methods=['POST'])
def send_message():
    if not session.get('logged_in'):
        return render_template('login.html', error=None)
    user_message = request.form['message']
    topics = request.form.getlist('topic[]') 
    
    capture_output = io.StringIO()
    original_stdout = sys.stdout
    sys.stdout = capture_output
    
    if topics:
        topic_string = ', '.join(topics)
        ai_message = agent_executor.run(f"{user_message} in {topic_string} Table.")
        user_message_f = f"{user_message} in {topic_string} Table."
    else:
        user_message_f = f"{user_message}"
        ai_message = agent_executor.run(f"{user_message}")
        
    sys.stdout = original_stdout
    operation = capture_output.getvalue().strip()
    log_write(user_message_f,ai_message,operation)
    return jsonify({'message': user_message, 'reply': ai_message})

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host='0.0.0.0')
