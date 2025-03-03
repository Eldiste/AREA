FROM python:3.12-slim

WORKDIR /app

# Copy project files
COPY . /app

RUN pip install --no-cache-dir --upgrade pip
RUN pip install -e .

# Install uvicorn explicitly
RUN pip install uvicorn

EXPOSE 8080

# Command to run the app
CMD ["uvicorn", "src.web.controllers.main:app", "--host", "0.0.0.0", "--port", "8080"]
