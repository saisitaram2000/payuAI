import vanna
from vanna.remote import VannaDefault
from vanna.flask import VannaFlaskApp

vn = VannaDefault(model='mistral', api_key=vanna.get_api_key('subhadipnandyofficial@gmail.com'))
vn.connect_to_mysql(host='10.248.7.33', dbname='payu', user='root', password='root', port=3306)

VannaFlaskApp(vn).run()