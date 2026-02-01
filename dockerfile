FROM python:3.11-slim

WORKDIR /app

COPY . .

RUN pip install pandas requests openpyxl

ENV PYTHONPATH="/app/Data/scripts"

CMD ["python", "main.py"]
