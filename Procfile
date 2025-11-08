#web: uvicorn api:app --host 0.0.0.0 --port $PORT
web: npm install && npm run build && pip install -r requirements.txt && python3 -m uvicorn api:app --host 0.0.0.0 --port $PORT