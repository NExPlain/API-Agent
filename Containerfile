FROM python:3.7-alpine
COPY . /app
WORKDIR /app
RUN pip install .
RUN api_gpt create-db
RUN api_gpt populate-db
RUN api_gpt add-user -u admin -p admin
EXPOSE 5000
CMD ["api_gpt", "run"]
