from typing import List, Union, Generator, Iterator
from pydantic import BaseModel
import os
import requests
import json
import time

class Pipeline:
    class Valves(BaseModel):
        DIFY_API_KEY: str = ""
        pass

    def __init__(self):
        self.name = "Dify Pipeline"
        self.valves = self.Valves(
            **{
                "DIFY_API_KEY": os.getenv(
                    "DIFY_API_KEY", "your-dify-api-key-here"
                )
            }
        )
        pass

    async def on_startup(self):
        print(f"on_startup:{__name__}")
        pass

    async def on_shutdown(self):
        print(f"on_shutdown:{__name__}")
        pass

    def pipe(
        self, user_message: str, model_id: str, messages: List[dict], body: dict
    ) -> Union[str, Generator, Iterator]:
        print(f"pipe:{__name__}")

        print(messages)
        print(user_message)

        DIFY_API_KEY = self.valves.DIFY_API_KEY

        headers = {
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        }

        # Construct payload for Dify API
        payload = {
            "query": user_message,
            "inputs": {},  # You can add any additional variables here
            "response_mode": "streaming" if body.get("stream", False) else "blocking",
            "user": "unique_user_id",  # You might want to customize this
            "auto_generate_name": True
        }

        # If there's a conversation ID, include it in the payload
        if "conversation_id" in body:
            payload["conversation_id"] = body["conversation_id"]

        try:
            r = requests.post(
                url="http://124.221.2.138/v1/chat-messages",
                json=payload,
                headers=headers,
                stream=body.get("stream", False),
            )

            r.raise_for_status()

            if body.get("stream", False):
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
                                # Yield buffered content periodically
                                if len(buffer) > 50:
                                    yield buffer
                                    buffer = ""
                        except json.JSONDecodeError:
                            continue
                if buffer:
                    yield buffer
            else:
                return r.json()
        except Exception as e:
            return f"Error: {e}"
