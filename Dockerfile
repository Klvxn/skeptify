FROM python:3.11.2-slim-buster

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

WORKDIR /usr/src/myapp

COPY requirements.txt ./

RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements.txt

COPY . .

RUN python manage.py migrate && python manage.py collectstatic

EXPOSE 8080

CMD ["waitress-serve", "--port=8080", "config.wsgi:application"]
