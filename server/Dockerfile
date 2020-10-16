FROM python:3.8-buster

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /app
ADD . /app

RUN chmod +x startup.sh

EXPOSE 8000

ENV PYTHONPATH=/app

CMD ["/app/startup.sh"]


