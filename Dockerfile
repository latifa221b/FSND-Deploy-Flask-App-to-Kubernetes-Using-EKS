FROM nikolaik/python-nodejs:python3.7-nodejs14-stretch	

COPY . /app

WORKDIR /app
COPY package*.json ./

RUN npm install @aws-cdk/aws-ssm 
RUN pip install --upgrade pip
RUN pip install flask
RUN pip install -r requirements.txt


ENTRYPOINT ["gunicorn", "-b", ":8080", "main:APP"]

