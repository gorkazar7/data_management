# Use the official Python image from the Docker Hub
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

COPY ./app /app

RUN pip install --no-cache-dir -r requirements.txt
RUN pip install fastapi uvicorn

# Expose the port on which the app will run in cloud
EXPOSE 8080

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]