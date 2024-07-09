# Use the official Python image from the Docker Hub
FROM python:3.9

COPY ./app /app

RUN pip install --no-cache-dir -r /app/requirements.txt

# Expose the port on which the app will run
EXPOSE 8000

# Command to run the FastAPI app using uvicorn
CMD ["uvicorn", "/app/main:app", "--host", "0.0.0.0", "--port", "8000"]