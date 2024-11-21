import boto3

from vanna.ollama import Ollama
from vanna.chromadb import ChromaDB_VectorStore

# session = boto3.Session()
# boto3_bedrock = boto3.client(service_name="bedrock-runtime")


class PayuAiInit(ChromaDB_VectorStore, Ollama):
    def __init__(self, config=None):
        ChromaDB_VectorStore.__init__(self, config=config)
        Ollama.__init__(self, config=config)

vn = PayuAiInit(config={'model': 'mistral'})

vn.train(
    documentation="""The main table in this database is named `transaction`. 
    All SQL queries should refer to this table exactly as `transaction` without any suffixes and not consider `transactions`."""
)

vn.train(
    documentation="""The main table in this database is named `transaction`. 
    All attributes/columns should be picked from transaction table DDL which i have defined."""
)

vn.train(
    documentation="""follow below mapping for mode
    Treat creditcard AS CC, 
    Treat debitcard as DC 
    """
)


vn.train(
    documentation="""GMV
    GMV for one transaction is calculated as transaction_fee - discount. all these fields are present in `transaction` table.
    GMV will be calculated for only captured transactions.
    for calculation of GMV for last 1 day:
    we should do sum of GMV of all transactions which are captured in last 1 day
    for calculation of GMV for last 1 week:
    we should do sum of GMV of all transactions which are captured in last 1 week
    for calculation of GMV for last 1 month:
    we should do sum of GMV of all transactions which are captured in last 1 month
    """
)

vn.train(
    documentation="""SRT
    SRT means `Sucess Rate of Transactions` only
    SRT is calculated using this formula: Total count of status=captured transactions multiplied by 100 divided by Total Transactions
    SRT is also known as success rate
    status,merchantid can be found in transaction table
    for calculation of SRT for last 1 day:
    we should find SRT using above formula for last 1 day
    for calculation of SRT for last 1 week:
    we should find SRT using above formula for last 1 week
    for calculation of SRT for last 1 month:
    we should find SRT using above formula for last 1 month
    always return SRT in percentage by rounding of to one decimal place for example 53.2%
    """
)