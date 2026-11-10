FROM python:3.12-slim
RUN pip install --no-cache-dir yt-dlp==2026.10.26
WORKDIR /app
COPY app.py .
USER 65534:65534
EXPOSE 8080
CMD ["python", "app.py"]
