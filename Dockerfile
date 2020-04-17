FROM python:3.7

COPY requirements.txt /requirements.txt
COPY pullbug /pullbug
COPY examples/rocket_chat.py /rocket_chat.py
RUN pip install -r requirements.txt

CMD [ "python", "./rocket_chat.py" ]
