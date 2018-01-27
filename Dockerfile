 FROM python:3
 ENV PYTHONUNBUFFERED 1
 RUN pip install virtualenv
 RUN mkdir /mongo-connector
 WORKDIR /mongo-connector
 RUN virtualenv .
 RUN bin/pip install 'mongo-connector[elastic5]'
 CMD ["/mongo-connector/bin/mongo-connector", "--stdout", "-m",  "mongo:27017", "-t", "elasticsearch1:9200", "-d", "elastic2_doc_manager"]
