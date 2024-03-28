FROM python:3.12-alpine

RUN mkdir "WeatherBot"

WORKDIR WeatherBot

COPY req.txt /WeatherBot

RUN pip install -r req.txt

COPY src /WeatherBot
