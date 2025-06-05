FROM public.ecr.aws/lambda/python:latest

RUN microdnf update -y && \
    microdnf install -y \
        gcc \
        gcc-c++ \
        unixODBC \
        unixODBC-devel && \
    microdnf clean all

RUN curl -o /etc/yum.repos.d/msprod.repo https://packages.microsoft.com/config/rhel/9/prod.repo && \
ACCEPT_EULA=Y microdnf install -y msodbcsql18 mssql-tools18 && \
microdnf clean all

COPY requirements.txt .

RUN pip install -r requirements.txt

COPY lambda_handlers.py .
COPY etl_controller.py .
COPY extract.py .
COPY transform.py .
COPY load.py .
COPY utilities.py .

CMD ["lambda_handlers.etl_lambda_handler"]