FROM python:3.7

COPY requirements.txt /
RUN pip install -r requirements.txt

# Swap in any of the source files to your liking
COPY src/pull_bug_gitlab_rc.py /
COPY .env /

CMD [ "python", "./pull_bug_gitlab_rc.py" ]
