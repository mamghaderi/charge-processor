FROM python:3.8

EXPOSE 8002

WORKDIR /app
COPY ./charge charge
COPY ./requirements.txt requirements.txt
COPY ./tests tests

RUN pip install -r requirements.txt

CMD ["gunicorn", "-b", "0.0.0.0:80", "charge.app:app"]