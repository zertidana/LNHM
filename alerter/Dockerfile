FROM public.ecr.aws/lambda/python:latest

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY send_alerts.py .
COPY utilities.py .

CMD ["send_alerts.alerter_lambda_handler"]
