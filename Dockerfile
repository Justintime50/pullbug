FROM python:3.7

COPY requirements.txt /
COPY src/rocket-chat/pull_bug_gitlab.py /
COPY src/rocket-chat/pull_bug_github.py /
COPY pull-bug.sh /
RUN pip install -r requirements.txt

CMD [ "./pull-bug.sh" ]
