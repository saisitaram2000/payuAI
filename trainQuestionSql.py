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
    question="""find SRT of merchant 180012 for last 1 week?""",
    sql="""/* we have transaction table, from this table we can find SRT
    */
    SELECT 
    (COUNT(CASE WHEN status = 'captured' THEN 1 END) * 100.0 / COUNT(*)) AS SRT
    FROM 
        transaction
    WHERE 
        merchantid = 180012 AND addedon >= NOW() - INTERVAL 7 DAY"""
)

vn.train(
    question="""find SRT of merchant 180012 on creditcard for last 1 week?""",
    sql="""/* we have transaction table, from this table we can find SRT on specific mode like creditcard
    */
    SELECT 
    (COUNT(CASE WHEN status = 'captured' AND mode = 'CC' THEN 1 END) * 100.0 / COUNT(*)) AS SRT
    FROM 
        transaction
    WHERE 
        merchantid = 180012 AND mode = 'CC' AND addedon >= NOW() - INTERVAL 7 DAY"""
)

vn.train(
    question="""find SRT of merchant 180012 on debitcard for last 1 week?""",
    sql="""/* we have transaction table, from this table we can find SRT on specific mode like creditcard
    */
    SELECT 
    (COUNT(CASE WHEN status = 'captured' AND mode = 'DC' THEN 1 END) * 100.0 / COUNT(*)) AS SRT
    FROM 
        transaction
    WHERE 
        merchantid = 180012 AND mode = 'DC' AND addedon >= NOW() - INTERVAL 7 DAY"""
)