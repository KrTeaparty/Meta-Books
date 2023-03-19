import requests
import json
import openai
from PyKakao import KoGPT, Karlo

def test_clova(API_KEYS: dict, content: str):
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
    if(rescode == 200):
        print(response.text)
    else:
        print("Error :", response.text)

def test_apenai(API_KEYS: dict, content: str):
    openai.api_key = API_KEYS['openai_api_key']
    prompt = "이 독후감을 요약해줘\n" + content
    response = openai.Completion.create(
        engine = "davinci", # 사용할 GPT 엔진
        prompt = prompt,    # API에 보낼 텍스트
        n = 1,              # 생성할 응답의 개수
        temperature = 0.5   # 낮은 온도로 설정하면 덜 일관적이고 안정적인 응답 생성
    )
    print(response)
    print(response.choices[0].text.strip())

def test_kogpt(API_KEYS: dict, content: str, ans_type: str):
    if ans_type == '키워드 추출':
        example = """
        연금술사     지은이-파울로코엘료
        연금술사란무엇일까?
        단지철이나납을금으로 바꾸는신비로은작업을가리키는걸까? 
        양치기산티아고는 늙은 왕을만나면서 이루어가는꿈의보석을바로 코앞에 두고 ,길고깊은여행을 떠났다.
        양치기산티아고가 이집트로 가던중 만난 영국인을만나면서 연금술사에대한 가치를알고 "위대한업"에 궁금증을가졌다. 
        나도사실 "연금술사:","위대한업", "자아신화","만물의언어" 이런것을의 의미를 아직은 잘알지못한다.
        하지만 산티아고가 떠난여행에서의  소망-꿈-환희를 절실히느꼈다.
        마지막으로산티아고는 코 앞에잇는진실한보석을온몸으로 느꼈다.
        그런산티아고가 부럽다. 이책을 읽으며 꿈을이뤄야겄다는 자신감이 더욱 생겨났다
        키워드 5개 추출: 연금술사, 여행, 자아 발견, 꿈, 적극적인 태도

        """
        prompt = "다음 독후감에서 키워드를 추출한다.\n\n" + example + content + "\n\n키워드 5개 추출: "

    elif ans_type == '번역':
        example = """
        문장, 악몽, 회사, 대학교, 하늘
        영어로 번역: sentence, nightmare, company, university, sky

        """
        prompt = "다음을 영어로 번역한다.\n\n" + example + content + "\n\n영어로 번역: "

    max_tokens = 30
    api = KoGPT(service_key = API_KEYS['kakao_rest_api_key'])

    result = api.generate(prompt, max_tokens, temperature=0.1)
    result = result['generations'][0]['text'].split('\n')[0].strip()
    return result

def test_karlo(API_KEYS: dict, content: str):
    api = Karlo(service_key = API_KEYS['kakao_rest_api_key'])
    translated_content = test_kogpt(API_KEYS, content, "번역")

    img_dict = api.text_to_image(translated_content, 1)

    img_str = img_dict.get("images")[0].get('image')

    img = api.string_to_image(base64_string = img_str, mode = 'RGBA')

    img.save('./test.png')


if __name__ == '__main__':
    with open('API_KEYS.json', 'r') as f:
        API_KEYS = json.load(f)

    test_contents = "안네의 일기는 최고의 일기야!"
    test_gpt_contents = """
    제목: 로빈스 크루소
    나는 이책을 읽고 나서 내가 쓰고있는 공책과 연필이 너무 소중하게 느껴졌다.
    문명과 격리된 무인도에서 살아가는데에 필요한것을 스스로 찾고 만들어 내며 28년을 산 로빈스 크루소의 끊임없는 개척 정신은 정말 놀라웠다.
    통나무배 하나를 만들기 위하여 20일이나 걸리며 나무를 배어 가지를 쳐내며 배모양을 만드는데 몇달이 걸렸다. 그러나 배가 너무 커서 바다까지 끌고 갈수없었다,
    이러한 실패를 거듭하면서 고향으로 갈수있다는 희망을 버리지 않는 그의 의지력은 큰 감동을 주었다.
    인간이 혼자서는 살아가기라는 것은 힘들다는것도 느꼈다.
    작게는 가족이나 이웃,크게는 국가 사이에서 도우며 살아야 인간다운 생활을 할수 있을것이다.남에게 해을 끼치며 자기 이익만 생각하는 사람이 이책을 읽고 사람을 그리워하는 로빈스 크루소의 심정을 느꼈으면 좋겠다.
    그러면 우리 사회는 더욱 밝고 살기 좋은 세상이 될 것이다.
    """
    #test_clova(API_KEYS, test_contents)
    #test_apenai(API_KEYS, test_gpt_contents)
    response = test_kogpt(API_KEYS, test_gpt_contents, "키워드 추출")
    test_karlo(API_KEYS, response)
    

# 테스트용 독후감 출처: https://blog.naver.com/PostView.nhn?isHttpsRedirect=true&blogId=okdaesa&logNo=60134831634