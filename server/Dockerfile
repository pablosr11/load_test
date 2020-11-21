FROM python:3.8-buster

# Install pip requirements
ADD requirements.txt .
RUN python -m pip install -r requirements.txt

WORKDIR /server/
ADD . /server

RUN chmod +x startup.sh
RUN chmod +x startup-reload.sh

EXPOSE 8000

## TODO: Uvicorn doesnt find modules from /server with absolute paths
## Could modify WORKDIR as well, but keep an eye on alembic migrations
ENV PYTHONPATH=/

CMD ["/server/startup.sh"]


