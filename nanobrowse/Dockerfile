FROM python:3.9-slim

WORKDIR /app

# Install Python dependencies
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt

# Copy application files
COPY . .

CMD ["hypercorn", "app:app", "--bind", "0.0.0.0:5000"]

