from fastapi import FastAPI, Response, Request
from fastapi.openapi.utils import get_openapi
import slack_bot
import uvicorn

app = FastAPI(
    title="Swagger API",
    description="빠르고 쉽게 사용하기 위해 [Swagger API]를 운영합니다",
    version="0.1",
    )

@app.get("/")

def custom_openapi():
    if not app.openapi_schema:
        app.openapi_schema = get_openapi(
            title=app.title,
            version=app.version,
            openapi_version=app.openapi_version,
            description=app.description,
            terms_of_service=app.terms_of_service,
            contact=app.contact,
            license_info=app.license_info,
            routes=app.routes,
            tags=app.openapi_tags,
            servers=app.servers,
        )
        for _, method_item in app.openapi_schema.get('paths').items():
            for _, param in method_item.items():
                responses = param.get('responses')
                # remove 422 response, also can remove other status code
                if '422' in responses:
                    del responses['422']
    return app.openapi_schema

app.openapi = custom_openapi


@app.post("/post/bot", summary="Bot",
        description="멘션한 채널에 입력받은 명령어의 실행 결과를 공유합니다.",  tags=['Bot'],
        responses={
        200: {
                "description": "null",
                "content": {
                    "application/json": {
                            "example": {
                                    }
                                    }
                            
                            } 
                }
                }
        )
async def bot(request:Request):
    event_data = await request.json()
    if event_data['type'] == 'url_verification':
        challenge = event_data['challenge']
        return challenge
    if not request.headers.get('x-slack-retry-num') and (event := event_data.get('event')):
        try:
            if "event" in event_data:
                # 이벤트 처리
                print("request channel =",event_data['event']['channel'])
                print("request command =",event_data['event']['text'])
                print("request user =",event_data['event']['user'])
                slack_channel = event_data['event']['channel']
                slack_bot.bot_get_message_ts(slack_channel)
                message = "Success"
                headers = {"X-Slack-No-Retry": "1"}
            return Response(content=message, headers=headers)
        except(KeyError):
            print("KeyError")
            pass

if __name__ == '__main__':
    uvicorn.run(app, host="0.0.0.0", port=5000)