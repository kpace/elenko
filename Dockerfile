FROM python:3

COPY . /src

RUN pip install -r /src/requirements.txt

CMD ["python", "-u", "/src/elenko.py" ]
