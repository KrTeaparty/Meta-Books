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
        self.des_content = ''
        self.date = dt.datetime.now().strftime('%Y-%m-%d %H:%M')

    def insert_content(self, content):
        self.content = content

    def describe(self):
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
        self.des_content = ans

    def get_keywords(self):
        model = "gpt-3.5-turbo"
        print('\t 3단계 시작')
        messages = [
            {
                "role": "system",
                "content": "You are an assistant who is good at creating prompts for image creation."
            },
            {
                "role": "assistant",
                "content": self.des_content
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

    def test_openai(self):
        print('===== test_openai 시작 =====')
        self.describe()
        self.get_keywords()
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

def index(request):
    #template = loader.get_template('bookreport/index.html')
    #content = request.GET.get('bookreport_txt')
    #context = {}
    return render(request, 'bookreport/index.html')
    #return HttpResponse(template.render(context))
    #return HttpResponse("Bookreport")

def display_img(request):
    if request.method == 'POST':
        template = loader.get_template('bookreport/display_img.html')
        with open('./bookreport/API_KEYS.json', 'r') as f:
            API_KEYS = json.load(f)

            book = Book_report(API_KEYS)
            book.insert_content(request.POST['bookreport_txt'])
            book.test_openai()
            for i in range(5):
                try:
                    book.test_karlo()
                    break
                except:
                    book.get_keywords()
                    return redirect('http://127.0.0.1:8000/bookreport') # 에러 발생시 이동할 URL
            #book.insert_to_db()

            context = {
                "cls": book,
                "gen_img": book.image
            }
    return HttpResponse(template.render(context))
    #return redirect('bookreport/display_img', context)

def saving(request):
    if request.method == 'POST':
        template = loader.get_template('bookreport/db_list.html')
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
        template=loader.get_template('bookreport/regen_img.html')
        with open('./bookreport/API_KEYS.json', 'r') as f:
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