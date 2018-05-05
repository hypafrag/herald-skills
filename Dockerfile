FROM python:3-alpine

WORKDIR /srv
ADD requirements.txt requirements.txt
RUN apk add --update --no-cache gcc python3-dev musl-dev libffi-dev openssl-dev linux-headers && \
    pip install --no-cache-dir -r requirements.txt && \
    apk del gcc python3-dev musl-dev libffi-dev openssl-dev linux-headers
ADD . .
ENTRYPOINT ["python", "skills.py"]
