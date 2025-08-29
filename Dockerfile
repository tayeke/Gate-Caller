FROM python:3.10-bullseye
ARG FLASK_ENV=development
ENV FLASK_ENV=${FLASK_ENV}
COPY .env /app/.env
WORKDIR /app
COPY . .
RUN pip3 install -r requirements.txt
CMD [ "python3", "-m" , "flask", "run", "--host=0.0.0.0", "--port=5000"]
