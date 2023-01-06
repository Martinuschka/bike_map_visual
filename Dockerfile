# syntax=docker/dockerfile:1

FROM python:3.10-slim-bullseye

RUN useradd -ms /bin/bash user
USER user

WORKDIR /home/user

COPY requirements.txt .
RUN pip install -r requirements.txt && rm requirements.txt

COPY main.py .
COPY measurements.csv .

#EXPOSE 10000
#ENTRYPOINT["python", "main.py"]
CMD ["python","main.py"]