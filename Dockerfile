FROM arm32v6/python:3.6-alpine3.8
#FROM python:3.6-alpine3.8

COPY . /powmon
WORKDIR /powmon

RUN pip install -r requirements.txt

RUN python -m unittest tests/*

CMD ["python","-u","powmon_local.py","--device_id","pzem","--mqtt_bridge_hostname","mosquitto"]

