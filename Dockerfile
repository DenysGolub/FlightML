FROM python:3.13.1-slim AS builder  

WORKDIR /install  

COPY requirements.txt .  

RUN pip install --no-cache-dir --prefix=/install -r requirements.txt  

FROM python:3.13.1-slim
  

WORKDIR /app  

COPY --from=builder /install /usr/local  
COPY . .  

EXPOSE 5000  

ENTRYPOINT [ "streamlit run", "main.py" ]
