FROM python:3.11-slim
WORKDIR /app
COPY main.py .
EXPOSE 8081
USER 65534:65534
CMD ["python", "-u", "main.py"]
