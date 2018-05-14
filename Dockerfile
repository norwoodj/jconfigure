FROM python:3.6-alpine
LABEL maintainer="norwood.john.m@gmail.com"

ARG APP_DIR=/var/lib/jmn23/jconfigure
WORKDIR ${APP_DIR}

COPY setup.py .
COPY jconfigure ./jconfigure/
RUN pip install .

ENTRYPOINT ["python", "-m", "unittest", "discover"]
