FROM python:3.12-slim
WORKDIR /app

# Install dependencies
COPY kisanmind/requirements-streamlit.txt ./requirements-streamlit.txt
RUN apt-get update && apt-get install -y --no-install-recommends gcc && rm -rf /var/lib/apt/lists/* \
    && pip install --no-cache-dir -r requirements-streamlit.txt

# Copy the app
COPY kisanmind/streamlit_app.py ./streamlit_app.py

EXPOSE 8501

CMD ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.address", "0.0.0.0"]
