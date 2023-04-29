from django.template import loader
from django.shortcuts import render
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
        self.date = dt.datetime.now().strftime('%Y%m%d')

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
        print('\t 3단계 시작')
        messages = [
            {
                "role": "system",
                "content": "You are a helpful assistant who is good at translating."
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

        # 4. 키워드 추출
        print('\t 4단계 시작')
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
                "content": "Condense up to 7 outward description to focus on nouns and adjectives separated by ','. Do not answer by each keyword."
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

'''
사용법
book = Book_report(API_KEYS)

test_gpt_contents = """
독후감 내용
"""

book.insert_content(test_gpt_contents)
book.test_openai()
book.test_karlo()
book.insert_to_db()
'''

'''
불러오는 법
def get_image(img_str):
    api = Karlo(service_key = API_KEYS['kakao_rest_api_key'])
    image = api.string_to_image(base64_string = img_str, mode = 'RGBA')
    image.save('./Features/test.png')

conn = sqlite3.connect('./metabooks/db.sqlite3')
cur = conn.cursor()

sql = """SELECT * from book_report"""
cur.execute(sql)
record = cur.fetchall()

for r in record:
    get_image(r[3])

cur.close()
conn.close()
'''



def index(request):
    template = loader.get_template('bookreport/index.html')
    content = request.GET.get('bookreport_txt')
    context = {}

    if content == None:
        context = {}
    else:
        with open('./bookreport/API_KEYS.json', 'r') as f:
            API_KEYS = json.load(f)

        br = Book_Report()
        book = Book_report(API_KEYS)
        book.insert_content(content)
        book.test_openai()
        book.test_karlo()
        #book.insert_to_db()

        context = {
            "gen_img": book.image
        }

    return HttpResponse(template.render(context))
    #return HttpResponse("Bookreport")  