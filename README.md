## Virtualenv install instructions

    virtualenv PENV
    source PENV/bin/activate
    pip install -r requirements.txt


## Run tests

    pytest tests


## Configure the database

    python shortie/manage.py create_db
    python shortie/manage.py pop_db


## Running the development server

    supervisord -c etc/supervisor/conf.d/shortie-dev.conf


## cURL commands to run against the API

Save google.com and m.google.com to Jason Seaver's list of urls
        curl -X POST -H 'Content-Type: application/json' -d'{"urls": {"desktop":"https://google.com", "mobile": "https://m.google.com"}}' localhost:9001/api/v1/users/jason@seaver.com/urls
Request the shortened url for google.com belonging to Jason Seaver
        curl -X GET -H'User-Agent: Mozilla/5.0(iPad; U; CPU iPhone OS 3_2 like Mac OS X; en-us) AppleWebKit/531.21.10 (KHTML, like Gecko) Version/4.0.4 Mobile/7B314 Safari/531.21.10' localhost:9001/9ca01ce
Request a list of all Jason Seaver's urls
        curl -X GET localhost:5000/api/v1/users/jason@seaver.com/urls
