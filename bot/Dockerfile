FROM python:3.10.8

WORKDIR /usr/src/app

COPY requirements.txt ./

RUN apt-get -y update && apt-get -y upgrade
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

CMD [ "python", "./main.py" ]