FROM python:3.7

COPY ./setup.py /pullbug/setup.py
COPY ./README.md /pullbug/README.md
COPY ./pullbug /pullbug/pullbug
COPY ./examples/rocket_chat_message.py /pullbug/rocket_chat_message.py

WORKDIR /pullbug

RUN python setup.py install

CMD [ "python", "rocket_chat_message.py" ]
