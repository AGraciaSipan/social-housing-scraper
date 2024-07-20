FROM python:3.12-slim AS base

RUN apt-get update && apt-get install -y \
    default-jdk \
    && apt-get clean

ENV JAVA_HOME=/usr/lib/jvm/java-11-openjdk-amd64
ENV PATH=$JAVA_HOME/bin:$PATH

RUN useradd -ms /bin/bash newuser

ADD ./src /home/newuser/house-scraper

WORKDIR /home/newuser/house-scraper

EXPOSE 8080

RUN pip install -r ./requirements.txt
RUN rm ./requirements.txt

FROM base AS dev

ADD ./dev-requirements.txt /home/newuser/house-scraper/dev-requirements.txt
RUN pip install -r ./dev-requirements.txt
RUN rm ./dev-requirements.txt

CMD ["tail", "-f", "/dev/null"]
