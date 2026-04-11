FROM python:3.10-bullseye
WORKDIR /GANI
COPY requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt
COPY . /GANI
CMD [ "python", "startup.py" ]
EXPOSE 5000