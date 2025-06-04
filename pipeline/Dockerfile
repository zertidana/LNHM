FROM python
COPY requirements.txt .
RUN pip3 install -r requirements.txt
COPY extract.py .
COPY transform.py .
COPY load.py .
CMD ["python", "load.py"]