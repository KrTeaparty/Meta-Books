from django.shortcuts import render
from django.http import HttpResponse

def index(request):
  return render(request,'myroom/index.html')

def popup(request):
  return render(request,'myroom/popup.html')


# diary
from django.template import loader
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

def diary(request):
  template = loader.get_template('myroom/diary.html')
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

#Book Report
def bookreport(request):
  return render(request,'myroom/bookreport.html')

 
from django.template import loader
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Book_Report
#from PIL import Image
#import io
import requests
import json
import openai
from PyKakao import Karlo
import sqlite3
import datetime as dt

class Book_report():
    def __init__(self, API_KEYS: dict):
        self.API_KEYS = API_KEYS
        self.uid = 1
        self.content = ''
        self.keywords = ''
        self.image = None
        self.date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')

    def insert_content(self, content):
        self.content = content

    def test_openai(self):
        print('===== test_openai 시작 =====')
        openai.api_key = self.API_KEYS['openai_api_key']
        model = "gpt-3.5-turbo"

        print('\t 1단계 시작')
        # 1. 독후감 묘사
        query = "아래 독후감의 명장면을 묘사해주세요." + self.content
        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content":query}
        ]
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages,  # API에 보낼 텍스트
        )
        ans = response['choices'][0]['message']['content']
        
        # 2. 답변 상세화
        print('\t 2단계 시작')
        messages.append(
            {
                "role": "assistant",
                "content": ans
            },
        )
        messages.append(
            {
                "role": "user",
                "content": "위 내용을 바탕으로 전체적인 배경과 외형적인 모습을 더 자세히 상상해서 묘사해주세요."
            }
        )
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        ans = response['choices'][0]['message']['content']

        # 3. 번역
        '''
        print('\t 3단계 시작')
        messages = [
            {
                "role": "system",
                "content": "You are an assistant who is good at creating prompts for image creation."
            },
            {
                "role": "assistant",
                "content": ans
            }
        ]
        messages.append(
            {
                "role": "user",
                "content": "영어로 번역해주세요."
            }
        )
        response = openai.ChatCompletion.create(
            model = model,
            messages = messages
        )
        ans = response['choices'][0]['message']['content']
        '''
        # 4. 키워드 추출
        print('\t 3단계 시작')
        messages = [
            {
                "role": "system",
                "content": "You are an assistant who is good at creating prompts for image creation."
            },
            {
                "role": "assistant",
                "content": ans
            }
        ]
        # 사용자 메시지 추가
        messages.append(
            {
                "role": "user", 
                "content": "Condense up to 7 outward description to focus on nouns and adjectives separated by ',' according to the form 'word1, word2, ...'"
            }
        )
        # ChatGPT API 호출하기
        response = openai.ChatCompletion.create(
            model=model,
            messages=messages
        )
        # <수정 예정> DB에 추출한 키워드 저장 필요
        ans = response['choices'][0]['message']['content']
        self.keywords = ans
        print('\t 전체 단계 수행 완료: ', self.keywords)

    def test_karlo(self):
        print('===== test_karlo 시작 =====')
        api = Karlo(service_key = self.API_KEYS['kakao_rest_api_key'])

        prompt = ", concept art, 8K, ultra-detailed, illustration, Claude Monet"
        prompt = f"{self.keywords}{prompt}"

        img_dict = api.text_to_image(prompt, 1)

        img_str = img_dict.get("images")[0].get('image')

        self.image = img_str
        
        print('\t 이미지 생성 완료')

    def insert_to_db(self):
        print('==== DB에 삽입 시작 =====')
        conn = sqlite3.connect('./metabooks/db.sqlite3')
        cur = conn.cursor()
        input_data = (self.uid, self.content, self.keywords, self.image, self.date)
        sql = f'INSERT INTO book_report VALUES (?,?,?,?,?)'
        cur.execute(sql, input_data)
        conn.commit()
        print('\t DB에 삽입 완료')
        cur.close()
        conn.close()

    def get_image(self):
        api = Karlo(service_key = self.API_KEYS['kakao_rest_api_key'])
        image = api.string_to_image(base64_string = self.image, mode = 'RGBA')
        return image

def display_img(request):
    if request.method == 'POST':
        template = loader.get_template('myroom/display_img.html')
        with open('./myroom/API_KEYS.json', 'r') as f:
            API_KEYS = json.load(f)

            book = Book_report(API_KEYS)
            book.insert_content(request.POST['bookreport_txt'])
            book.test_openai()
            book.test_karlo()
            #book.insert_to_db()

            context = {
                "cls": book,
                "gen_img": book.image
            }
    return HttpResponse(template.render(context))
    #return redirect('bookreport/display_img', context)

def saving(request):
    if request.method == 'POST':
        template = loader.get_template('myroom/db_list.html')
        '''
        temp = {
            'content' : request.GET.get('content'),
            'keywords' : request.GET.get('keywords'),
            'date' : request.GET.get('date'),
            'img' : request.GET.get('image')
        }
        '''
        temp = {
            'content' : request.POST['content'],
            'keywords' : request.POST['keywords'],
            'date' : request.POST['date'],
            'img' : request.POST['image']
        }
            
        print(temp)
        br = Book_Report(content=temp['content'], keywords=temp['keywords'], image=temp['img'], date=temp['date'])
        br.save()
        context = {'contextlist': Book_Report.objects.all()}
    return HttpResponse(template.render(context))

def regen_img(request):
    if request.method == 'POST':
        template=loader.get_template('myroom/regen_img.html')
        with open('./myroom/API_KEYS.json', 'r') as f:
            API_KEYS = json.load(f)

            book = Book_report(API_KEYS)
            book.insert_content(request.POST['content'])
            book.keywords = request.POST['keywords']
            book.test_karlo()

        context ={
            "cls": book,
            "gen_img": book.image
        }

        return HttpResponse(template.render(context)) 