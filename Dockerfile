FROM --platform=linux/amd64 python:3.9-slim
WORKDIR /app

COPY config.yaml /app/config.yaml

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

#RUN pip install gunicorn
ENV STREAMLIT_ENV=app.py
EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8080"]
#CMD ["gunicorn", "-w", "1", "-b", "0.0.0.0:8080", "app.py:app.py"]