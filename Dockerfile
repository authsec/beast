FROM gilleslamiral/imapsync
LABEL maintainer="Jens Frey <jens.frey@coffeecrew.org>" Version="2021-08-08"

USER root
ARG DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get -y upgrade && apt-get -y install python3

COPY beast.py /bin

WORKDIR /beast

RUN chown nobody:nogroup /bin/beast.py && chown -R nobody:nogroup /beast

USER nobody:nogroup

ENTRYPOINT ["/usr/bin/python3","/bin/beast.py"]