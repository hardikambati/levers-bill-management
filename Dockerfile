FROM python:3.8.10-slim

ENV PYTHONUNBUFFERED=1

RUN mkdir /code

COPY . /code/

WORKDIR /code

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]