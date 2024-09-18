import random
import ssl
import urllib.parse
import certifi
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
import requests
import urllib.request
from fastapi import HTTPException
import platform
import sys
import os

sysOS = platform.system()
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from hoon_work import api_keys


def bot_get_message_ts(slack_channel):
    global get_text
    global channel
    global bot_token
    global request_user
    global permission

    member_list = ['U022XQUHUTZ']
    bot_token = api_keys.bot_token
    ssl_context = ssl.create_default_context(cafile=certifi.where())
    client = WebClient(token=bot_token, ssl=ssl_context)
    channel = slack_channel

    # 슬랙 채널 내 메세지 조회
    conversation_datas = client.conversations_history(channel=channel)

    # 채널 내 메세지 정보 활용을 위해 변수 선언
    messages = conversation_datas.data['messages'][0]
    message = messages['text']
    request_user = messages['user']

    try:
        split_message = message.split(' ')
        get_text = split_message
    except:
        get_text = message
        print("exception 발생,",get_text)

    # Request 유저 권한 판정
    for member in member_list:
        if member in request_user:
            print('request member is Member')
            permission = 'member'
            break
        else:
            permission = 'normal'


    if permission == "member":
        print("해당 권한으로 수행할 수 있습니다")
			
    else:
        print("해당 권한으로는 수행할 수 없습니다")
        text = "해당 권한으로는 이용할 수 없는 기능입니다.\n문의: <@U022XQUHUTZ>"
        requests.post("https://slack.com/api/chat.postMessage",
        headers={
            
            "Authorization": "Bearer " + bot_token
            
            },
        data={
            
            "channel":channel,
            "text": f"{text}"
            
            }
        )
        raise HTTPException(status_code=400, detail="Bad Request, 권한 외 사용")


    if channel != "C023CKG83CJ" and channel != "C023CKG83CJ":
        text = "지정된 채널에서만 이용해 주세요.\n지정 채널: <@C023CKG83CJ>\n초대 문의: <@U022XQUHUTZ>"
        requests.post("https://slack.com/api/chat.postMessage",
        headers={
            
            "Authorization": "Bearer " + bot_token
            
            },
        data={
            
            "channel":channel,
            "text": f"{text}"
            
            }
        )
        raise HTTPException(status_code=400, detail="Bad Request, 지정 채널 외의 이용")

    run(get_text, request_user)


def run(get_text, request_user):
    call = "<@{}>".format(request_user)

    # 룰렛 기능
    if get_text[1] == "룰렛":
        text = call+'\n'
        if len(get_text) == 3:

            # 입력 문자열을 쉼표로 분할하여 리스트로 변환
            input_string = get_text[2]
            input_list = input_string.split(',')
            
            text_list = []
            
            for item in input_list:
                item = item.strip()
                if item.isnumeric():
                    # 숫자인 경우 숫자 리스트에 추가
                    text_list.append(int(item))
                else:
                    # 숫자가 아닌 경우 리스트에 추가
                    text_list.append(item)
            
            if len(text_list) > 0:
                # 숫자 리스트에서 무작위로 선택
                random_num = random.choice(text_list)
                print("선택된 값: ", random_num)
                text += "결과 : *{}*".format(random_num)
        else:
            print("입력 값 오류 발생")
            text += "입력값을 다시 확인해 주세요."



    elif get_text[1] == "날씨":
        text = call+'\n'
        city = get_text[2]
        
        weather_key = api_keys.weather_api_key

        url = f"http://api.weatherapi.com/v1/current.json"
        params = {
            'key': weather_key,
            'q': city,
            'lang': 'kr'
        }
        response = requests.get(url, params=params)
        data = response.json()
        if 'current' in data:
            condition = data['current']['condition']['text']
            temp_c = data['current']['temp_c']
            text += f"{city}의 현재 날씨: {condition}, 온도: {temp_c}°C"
        else:
            text += f"오류: {data.get('error', {}).get('message', '알 수 없는 오류')}"



    # 예외 Case 및 환경 Print Handling
    else:
        print("올바른 명령어가 아닙니다.")
        text = "명령어를 인식하지 못했습니다.\n@Bot help 를 입력 시, 사용 설명서 링크를 받을 수 있습니다."


    if text == '' or text == None:
        text = '결과를 출력하지 못했습니다.\n명령어를 다시 확인해 주세요.\n@Bot help 를 입력 시, 사용 설명서 링크를 받을 수 있습니다.'

    else:
        # Slack Message 전송
        requests.post("https://slack.com/api/chat.postMessage",
        headers={
            
            "Authorization": "Bearer " + bot_token
            
            },
        data={
            
            "channel":channel,
            "text": f"{text}"
            
            }
        )