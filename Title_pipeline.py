from typing import List, Union
from pydantic import BaseModel
import os
import requests
import json
import uuid
import time

class Pipeline:
    class Valves(BaseModel):
        DIFY_API_KEY: str = ""
        pass

    def __init__(self):
        self.name = "Talk With The Developer"
        self.valves = self.Valves(
            **{
                "DIFY_API_KEY": os.getenv(
                    "DIFY_API_KEY", "your-dify-api-key-here"
                )
            }
        )
        print(f"Initialized Pipeline with API Key: {self.valves.DIFY_API_KEY}")
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, dict]:
        print(f"pipe:{__name__}")
        print(f"Received user_message: {user_message}")
        print(f"Received model_id: {model_id}")
        print(f"Received messages: {json.dumps(messages, indent=2)}")
        print(f"Received body: {json.dumps(body, indent=2)}")

        DIFY_API_KEY = self.valves.DIFY_API_KEY

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }
        print(f"Using headers: {headers}")

        payload = {
            "query": user_message,
            "response_mode": "blocking",  
            "user": "unique_user_id",  # 你可能需要改改这部分
            "auto_generate_name": True
        }

        if "conversation_id" in body and body["conversation_id"]:
            payload["conversation_id"] = body["conversation_id"]

        print(f"Constructed payload: {json.dumps(payload, indent=2)}")

        try:
            r = requests.post(
                url="http://110.xxx.248.xxx/v1/chat-messages",
                json=payload,
                headers=headers
            )

            print(f"Request sent to Dify API, status code: {r.status_code}")
            print(f"Response headers: {r.headers}")
            r.raise_for_status()

            response_json = r.json()
            print(f"Received response: {json.dumps(response_json, indent=2)}")

            # 将 Dify 的响应转换为 OpenAI 格式
            openai_response = {
                "id": response_json.get("message_id", str(uuid.uuid4())),
                "object": "chat.completion",
                "created": response_json.get("created_at", int(time.time())),
                "model": model_id,
                "choices": [
                    {
                        "message": {
                            "role": "assistant",
                            "content": response_json.get("answer", "")
                        },
                        "finish_reason": "stop"
                    }
                ],
                "usage": response_json.get("usage", {})
            }

            print(f"Final OpenAI compatible response: {json.dumps(openai_response, indent=2)}")

            return openai_response
        except requests.exceptions.RequestException as req_err:
            print(f"Request error: {req_err}")
            return f"Error: {req_err}"
        except Exception as e:
            print(f"Unexpected error: {e}")
            return f"Error: {e}"
