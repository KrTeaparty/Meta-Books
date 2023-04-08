from django.shortcuts import render
from django.http import HttpResponse
from django.template import loader
import requests
import json
import openai
from PyKakao import Karlo
import sqlite3
import datetime as dt

class Book_report():
    def __init__(self, API_KEYS: dict):
        self.API_KEYS = API_KEYS
        openai.api_key = API_KEYS['openai_api_key']
        self.conn = sqlite3.connect('../db.sqlite3')
        self.cur = self.conn.cursor()
        self.uid = 1
        self.content = ''
        self.keywords = ''
        self.image = None
        self.date = dt.datetime.now().strftime('%Y%m%d')

    def test_openai(self):
        model = "gpt-3.5-turbo"

        # 1. 독후감 묘사
        query = "아래 독후감의 명장면을 묘사해주세요." + content
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
        return ans




def test_openai(API_KEYS: dict, content: str):
  openai.api_key = API_KEYS['openai_api_key']
  conn, cur = connect_db()
  model = "gpt-3.5-turbo"

  # 1. 독후감 묘사
  query = "아래 독후감의 명장면을 묘사해주세요." + content
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
  return ans

def test_karlo(API_KEYS: dict, content: str):
  api = Karlo(service_key = API_KEYS['kakao_rest_api_key'])
  prompt = ", concept art, 8K, ultra-detailed, illustration, Claude Monet"
  prompt = f"{content}{prompt}"

  img_dict = api.text_to_image(prompt, 1)

  img_str = img_dict.get("images")[0].get('image')

  img = api.string_to_image(base64_string = img_str, mode = 'RGBA')


  return img
  # <수정 예정> 저장 경로 결정 필요
  #img.save('./Features/test.png')

def insert_content(UID, contents):
  conn, cur = connect_db()
  sql = 

def index(request):
  template = loader.get_template('bookreport/index.html')
  
  context={}
  
  
  return HttpResponse(template.render(context,request))  