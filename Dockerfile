FROM python:3.7

COPY requirements.txt /
COPY src/pull_bug_gitlab_rc.py /
RUN pip install -r requirements.txt

CMD [ "python", "./pull_bug_gitlab_rc.py" ]
