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
  `txnid` bigint(20) unsigned NOT NULL AUTO_INCREMENT  This is unique id for any transaction represents uniquely for single transaction, for example: 3,
  `merchantid` int(10) unsigned NOT NULL  This is unique id provided by payu to its merchants like flipkart,amazon etc but in this table its not unique id,
  `transaction_fee` decimal(15,2) NOT NULL  This is transaction amount on which merchant has initiated transaction with,
  `discount` decimal(15,2) DEFAULT '0.00' This is discount amount applied on transaction like offer discount or NoCostEMI discount,
  `amount` decimal(15,2) NOT NULL This is net debit amount i.e ideally its transaction_fee - discount,
  `paymentgatewayid` bigint(20) unsigned DEFAULT NULL This is unique id assigned for each paymentgateway by payu, but this is not unique in this table,
  `mode` varchar(20) DEFAULT NULL  This is payment mode of transaction for example: CC,DC,emi,upi,wallet,
  `status` varchar(20) NOT NULL  This is transaction status for example: captured,failed,bounced,dropped,userCancelled  captured means transaction is success, failed means transaction is failed, userCancelled means where user has cancelled the transaction on checkoutpage
  `error_message` varchar(1000) DEFAULT NULL This signifies what is reason of transaction failure for example Technical Failure,
  `addedon` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP' This is time at which transaction is created into table and also it is transaction initiation time mostly we will be using this column for any date filters
  PRIMARY KEY (`txnid`),
  KEY `phone_idx` (`phone`),
  KEY `idx_merchantid_addedon_status` (`merchantid`,`addedon`,`status`),
  KEY `idx_addedon_status` (`addedon`,`status`)

) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
""")

vn.train(
  ddl="""
  CREATE TABLE `merchant` (
  `id` int(10) unsigned NOT NULL AUTO_INCREMENT  This is unique id for merchant also called as merchantid,
  `name` varchar(50) NOT NULL  This is name of the merchant for example flipkart,amazon,
  `phone` varchar(20) DEFAULT NULL This is phone number of merchant we use this phone during authentication,
  `active` tinyint(1) NOT NULL DEFAULT '0' whether merchant is active or inactive 1 means active 0 means inactive,
  `addedon` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP This is time at which merchant onboarded,
  `paymentGateway` MEDIUMTEXT This is comma seperated paymentgateways which signifies what all paymentgateways are enabled for this merchant for example: AXIS,HDFC,SBI,ICICI,
  `paymentMode` MEDIUMTEXT This is comma seperated paymentmodes which signifies what all paymentmodes are enabled for this merchant for example: CC,DC,EMI,UPI ,
   PRIMARY KEY (`id`),
) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
  """)

# vn.train(
#   ddl="""
#   CREATE TABLE `` (
#   `id` int(10) unsigned NOT NULL AUTO_INCREMENT  This is unique id for merchant also called as merchantid,
#   `name` varchar(50) NOT NULL  This is name of the merchant for example flipkart,amazon,
#   `phone` varchar(20) DEFAULT NULL This is phone number of merchant we use this phone during authentication,
#   `active` tinyint(1) NOT NULL DEFAULT '0' whether merchant is active or inactive 1 means active 0 means inactive,
#   `addedon` timestamp NOT NULL DEFAULT CURRENT_TIMESTAMP This is time at which merchant onboarded,
#   `paymentGateway` MEDIUMTEXT This is comma seperated paymentgateways which signifies what all paymentgateways are enabled for this merchant for example: AXIS,HDFC,SBI,ICICI,
#   `paymentMode` MEDIUMTEXT This is comma seperated paymentmodes which signifies what all paymentmodes are enabled for this merchant for example: CC,DC,EMI,UPI ,
#    PRIMARY KEY (`id`),
# ) ENGINE=InnoDB AUTO_INCREMENT=1 DEFAULT CHARSET=latin1;
#   """)