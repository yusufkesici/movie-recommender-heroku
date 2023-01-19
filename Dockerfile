FROM python:3.8

COPY . /UI_Recommender

WORKDIR /UI_Recommender

RUN pip install --upgrade pip
RUN pip install -r requirements.txt

EXPOSE 3000

CMD ["python", "UI_Recommender.py"]
