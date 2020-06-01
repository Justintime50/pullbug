FROM python:3.7

COPY ./setup.py /pullbug/setup.py
COPY ./README.md /pullbug/README.md
COPY ./pullbug /pullbug/pullbug
COPY ./examples/slack.py /pullbug/slack.py

WORKDIR /pullbug

RUN python setup.py install

CMD [ "python", "slack.py" ]
