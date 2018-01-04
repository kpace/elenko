FROM python:3

COPY . /src

RUN pip install -r /src/requirements.txt

ARG slack_token
ENV ELENKO_SLACK_TOKEN=$slack_token

CMD ["python", "/src/elenko.py" ]
