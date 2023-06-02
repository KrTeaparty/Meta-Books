from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
from .models import Diary
import requests
import json
import statistics
import datetime as dt


def test_clova(API_KEYS,content):
  url = "https://naveropenapi.apigw.ntruss.com/sentiment-analysis/v1/analyze"

  headers = {
    "X-NCP-APIGW-API-KEY-ID": API_KEYS['clova_client_id'],
    "X-NCP-APIGW-API-KEY": API_KEYS['clova_client_secret'],
    "Content-Type": "application/json"
  }
  
  data = {
    "content": content
  }

  response = requests.post(url, data=json.dumps(data), headers=headers)
  rescode = response.status_code
  if (rescode == 200):
    result = json.loads(response.text)
  else:
    result = "Error :"+response.text
    
  return result




def index(request):
  template = loader.get_template('diary/index.html')
  content = request.GET.get('diary_txt')
  long_content = []
  context = {}
  page = 1
  
  if content == None:
    context = {}
  elif len(content) > 1000:
    with open('./diary/API_KEYS.json', 'r') as f:
      API_KEYS = json.load(f)
  
    context = {
        "txt_data" : content,
        "sentiment" : "Null",
        "pos" : "Null",
        "neu" : "Null",
        "neg" : "Null",
      }
    page = len(content) // 1000
    prev_idx = 0
    idx = 1000
    while True:
      idx = content[prev_idx:idx].rfind('.')
      if idx == -1:
        break
      long_content.append(content[prev_idx:idx])
      prev_idx = idx

    sentiment_list = []
    pos_list = []
    neu_list = []
    neg_list= []

    for i in range(0, page):
      result = test_clova(API_KEYS, long_content[i])
      sentiment_list.append(result['document']['sentiment'])
      pos_list.append(result['document']['confidence']['positive'])
      neu_list.append(result['document']['confidence']['neutral'])
      neg_list.append(result['document']['confidence']['negative'])

    sentiment = statistics.mode(sentiment_list)
    pos = statistics.mean(pos_list)
    neu = statistics.mean(neu_list)
    neg = statistics.mean(neg_list)

    context = {
      "txt_data": content,
      "sentiment": sentiment,
      "pos" : pos,
      "neu" : neu,
      "neg" : neg,
    }

    diary = Diary(content=context['txt_data'], senti=context['sentiment'], 
                  pos=context['pos'], neu=context['neu'], neg=context['neg'], 
                  date=dt.datetime.now().strftime('%Y-%m-%d %H:%M'))
    diary.save()

  else:
    with open('./diary/API_KEYS.json', 'r') as f:
      API_KEYS = json.load(f)
  
    context = {
        "txt_data" : content,
        "sentiment" : "Null",
        "pos" : "Null",
        "neu" : "Null",
        "neg" : "Null",
      }
    result = test_clova(API_KEYS, content)
    sentiment = result['document']['sentiment']
    pos = result['document']['confidence']['positive']
    neu = result['document']['confidence']['neutral']
    neg = result['document']['confidence']['negative']

    context = {
      "txt_data": content,
      "sentiment": sentiment,
      "pos" : pos,
      "neu" : neu,
      "neg" : neg,
    }

    diary = Diary(content=context['txt_data'], senti=context['sentiment'], 
                  pos=context['pos'], neu=context['neu'], neg=context['neg'],
                  date=dt.datetime.now().strftime('%Y-%m-%d %H:%M'))
    diary.save()
  
  return HttpResponse(template.render(context, request))