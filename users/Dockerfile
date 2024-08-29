FROM python:3.11-slim

RUN apt-get update
RUN apt-get install -y gcc libpq-dev

WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .
COPY public_key.pem .
COPY private_key.pem .

# Install any dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the source code into the container
COPY ./src /app

# Expose the port FastAPI will run on
EXPOSE 8001

# Command to run the FastAPI app using Uvicorn
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8001"]
