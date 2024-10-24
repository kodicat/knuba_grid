FROM python:3.9
WORKDIR /usr/local/app

COPY ./requirements.txt ./
RUN pip install --no-cache-dir -r ./requirements.txt

COPY . ./src

RUN useradd app
USER app

CMD [ "python", "./src/run.py" ]