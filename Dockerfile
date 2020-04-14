FROM python:3.7

COPY requirements.txt /
COPY pullbug /
COPY example.py /
RUN pip install -r requirements.txt

CMD [ "python" "./example.py" ]
