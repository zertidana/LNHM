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

COPY archive_plant_reading.py .
COPY utilities.py .

CMD ["archive_plant_reading.archive_lambda_handler"]
