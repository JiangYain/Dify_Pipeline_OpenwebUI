import os
import requests
import json
import time
from typing import List, Union, Generator, Iterator, Optional, Dict
from pydantic import BaseModel

class Pipeline:
    class Valves(BaseModel):
        DIFY_API_KEY: str = ""

    def __init__(self):
        self.name = "Dify Pipeline"
        self.valves = self.Valves(
            **{
                "DIFY_API_KEY": os.getenv(
                    "DIFY_API_KEY", "your-dify-api-key-here"
                )
            }
        )
        self.chat_id = None
        self.chat_id_to_conversation_id: Dict[str, str] = {}

    async def on_startup(self):
        print(f"on_startup:{__name__}")

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")

    async def inlet(self, body: dict, user: Optional[dict] = None) -> dict:
        print(f"inlet:{__name__}")
        print(f"user: {user}")
        print(f"body: {body}")
        # Store the chat_id from body
        self.chat_id = body.get("chat_id")
        print(f"Stored chat_id: {self.chat_id}")
        return body

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")
        print(f"chat_id available in pipe: {self.chat_id}")
        print(f"messages: {messages}")
        print(f"user_message: {user_message}")

        DIFY_API_KEY = self.valves.DIFY_API_KEY

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        payload = {
            "query": user_message,
            "inputs": {},
            "response_mode": "streaming" if body.get("stream", False) else "blocking",
            "user": "unique_user_id",
            "auto_generate_name": True
        }

        if self.chat_id and self.chat_id in self.chat_id_to_conversation_id:
            payload["conversation_id"] = self.chat_id_to_conversation_id[self.chat_id]
            print(f"Using existing conversation_id: {payload['conversation_id']} for chat_id: {self.chat_id}")
        else:
            print(f"No existing conversation_id for chat_id: {self.chat_id}")

        try:
            r = requests.post(
                url="http://124.xx1.2.xxx/v1/chat-messages",
                json=payload,
                headers=headers,
                stream=body.get("stream", False),
            )

            r.raise_for_status()

            if body.get("stream", False):
                return self._handle_streaming_response(r)
            else:
                return self._handle_blocking_response(r)
        except Exception as e:
            print(f"Error in pipe: {e}")
            return f"Error: {e}"

    def _handle_streaming_response(self, r):
        buffer = ""
        for line in r.iter_lines():
            if line:
                decoded_line = line.decode('utf-8').strip()
                if decoded_line.startswith('data: '):
                    decoded_line = decoded_line[len('data: '):]
                try:
                    json_line = json.loads(decoded_line)
                    if json_line.get("event") == "message":
                        buffer += json_line.get("answer", "")
                        if len(buffer) > 0:
                            yield buffer
                            buffer = ""
                            time.sleep(0.001)
                    elif json_line.get("event") == "message_end":
                        if self.chat_id and "conversation_id" in json_line:
                            self.chat_id_to_conversation_id[self.chat_id] = json_line["conversation_id"]
                            print(f"Stored conversation_id: {json_line['conversation_id']} for chat_id: {self.chat_id}")
                except json.JSONDecodeError:
                    continue
        if buffer:
            yield buffer

    def _handle_blocking_response(self, r):
        response = r.json()
        if self.chat_id and "conversation_id" in response:
            self.chat_id_to_conversation_id[self.chat_id] = response["conversation_id"]
            print(f"Stored conversation_id: {response['conversation_id']} for chat_id: {self.chat_id}")
        return response
