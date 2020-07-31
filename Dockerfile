FROM python:stretch

COPY . /app
WORKDIR /app

RUN bash \
    git \
    nodejs=10.16.3-r0 \
    npm=10.16.3-r0 &&\
    npm i @aws-cdk/aws-ssm 
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install -r requirements.txt


ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]

