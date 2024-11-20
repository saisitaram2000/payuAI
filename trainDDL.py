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
    ddl="""
    CREATE TABLE `transaction` (
  `id` bigint(20) unsigned NOT NULL AUTO_INCREMENT  This is unique id for any transaction which is also called as payuid represents uniquely for single transaction, for example: 90000019911801773,
  `merchantid` int(10) unsigned NOT NULL  This is unique id provided by payu to its merchants like flipkart,amazon etc but in this table its not unique id,
  `txnid` varchar(50) NOT NULL  This is id which merchants passes to payu when initiating transaction for example: 3174499cd4504d1bb90f,
  `transaction_fee` decimal(15,2) NOT NULL  This is transaction amount on which merchant has initiated transaction with,
  `discount` decimal(15,2) DEFAULT '0.00' This is discount amount applied on transaction like offer discount or NoCostEMI discount,
  `additional_charges` decimal(15,2) DEFAULT '0.00' This is convenience fee passed my merchant when initiating transaction this will be added to transaction amount,
  `amount` decimal(15,2) NOT NULL This is net debit amount i.e ideally its additional_charges + transaction_fee - discount,
  `paymentgatewayid` bigint(20) unsigned DEFAULT NULL This is unique id assigned for each paymentgateway by payu, but this is not unique in this table,
  `mode` varchar(20) DEFAULT NULL  This is payment mode of transaction for example: CC,DC,emi,upi,wallet,
  `status` varchar(20) NOT NULL  This is transaction status for example: captured,failed,bounced,dropped,userCancelled  captured means transaction is success, failed means transaction is failed, userCancelled means where user has cancelled the transaction on checkoutpage
  `reattempt_id` bigint(20) DEFAULT NULL This is also similar to id column but when any transaction is failed and user retried the transaction re-attempt id of retried transaction is parent transaction id,
  `base_id` bigint(20) NOT NULL DEFAULT '0' This is also similar to id column in case of split payments like DownPayment+ EMI for any child transaction base_id will be parent transaction id,
  `field9` varchar(1000) DEFAULT NULL This signifies what is reason of transaction failure for example Technical Failure,
  `addedon` timestamp NOT NULL DEFAULT '0000-00-00 00:00:00' This is time at which transaction is created into table and also it is transaction initiation time mostly we will be using this column for any date filters,
  `updatedon` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP This is final time at which transaction is success,failed or any updates happened. This is not a very important field and can be ignored for most of queries,
  PRIMARY KEY (`id`)

) ENGINE=InnoDB AUTO_INCREMENT=999000000001662 DEFAULT CHARSET=latin1;
""")