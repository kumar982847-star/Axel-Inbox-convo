FROM python:3.10

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
RUN python -m playwright install
CMD ["python", "app.py"]
