# last built on July 19 2025
FROM debian:bookworm

RUN apt-get update && \
    apt-get install -y python3-pip

# Allow installing stuff to system Python.
RUN rm -f /usr/lib/python3.11/EXTERNALLY-MANAGED

COPY image-search-app image-search-app
WORKDIR /image-search-app

RUN python3 -m pip install --no-deps -r requirements.txt
EXPOSE 8000
# ENTRYPOINT [ "/entrypoint.sh" ]
CMD [ "uvicorn", "main:app" ]