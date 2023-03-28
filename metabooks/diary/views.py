from django.shortcuts import render
from django.template import loader
from django.http import HttpResponse
import requests
import json


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
  template = loader.get_template('index.html')
  content = request.GET.get('diary_txt')
  context = {}
  
  if content == None:
    context = {}
  elif len(content) > 1000:
    context = {
      "txt_data" : content,
      "sentiment" : str(len(content)) + " characters in your diary. Please enter no more than 1000 characters",
      "pos" : "Null",
      "neu" : "Null",
      "neg" : "Null",
    }
  else:
    with open('./diary/API_KEYS.json', 'r') as f:
      API_KEYS = json.load(f)
  
    result = test_clova(API_KEYS,content)

    context = {
      "txt_data": content,
      "sentiment": result['document']['sentiment'],
      "pos" : result['document']['confidence']['positive'],
      "neu" : result['document']['confidence']['neutral'],
      "neg" : result['document']['confidence']['negative'],
    }
 
    
  
  return HttpResponse(template.render(context, request))