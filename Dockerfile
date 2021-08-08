FROM gilleslamiral/imapsync
LABEL maintainer="Jens Frey <jens.frey@coffeecrew.org>" Version="2021-08-08"

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get -y install python3

WORKDIR /beast
COPY beast.py /beast

RUN chown -R nobody:nogroup /beast

USER nobody:nogroup

ENTRYPOINT ["/usr/bin/python3","/beast/beast.py"]