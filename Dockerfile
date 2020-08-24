FROM python:3.8-alpine

RUN pip install --upgrade pip
RUN pip install requests==2.22.0

WORKDIR /app
COPY ./pr_status_action.py .

CMD ["python3", "/app/pr_status_action.py"]
