import os
import requests
import subprocess

from openai import OpenAI
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# 🔑 API 키 환경변수 불러오기
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
ELEVEN_API_KEY = os.getenv("ELEVEN_API_KEY")

# OpenAI 연결
client = OpenAI(api_key=OPENAI_API_KEY)
print(OPENAI_API_KEY)
print(ELEVEN_API_KEY)

TOPIC = "철학이란 무엇인가?"

script_prompt = f"""
여성 1인 진행 철학 유튜브 대본 작성.
주제: {TOPIC}
5~7분 분량.
구조:
1. 강렬한 질문
2. 철학자 사례
3. 현대 적용
4. 실천 질문
"""

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": script_prompt}]
)

script_text = response.choices[0].message.content

with open("script.txt", "w", encoding="utf-8") as f:
    f.write(script_text)

# 2️⃣ ElevenLabs 음성 생성
# voice_url = "https://api.elevenlabs.io/v1/text-to-speech/VOICE_ID"

# headers = {
#   "xi-api-key": ELEVEN_API_KEY,
#    "Content-Type": "application/json"
# }

# data = {
#    "text": script_text,
#    "voice_settings": {
#        "stability": 0.5,
#        "similarity_boost": 0.8
#    }
# }

# response = requests.post(voice_url, json=data, headers=headers)

# with open("voice.mp3", "wb") as f:
#    f.write(response.content)

# 3️⃣ 영상 합성 (background.mp4 준비 필요)
# subprocess.run([
#    "ffmpeg",
#    "-i", "background.mp4",
#    "-i", "voice.mp3",
#    "-c:v", "copy",
#    "-c:a", "aac",
#    "-shortest",
#    "final_video.mp4"
# ])

# 4️⃣ 유튜브 업로드
SCOPES = ["https://www.googleapis.com/auth/youtube.upload"]

flow = InstalledAppFlow.from_client_secrets_file(
    "client_secret.json", SCOPES)
credentials = flow.run_console()

youtube = build("youtube", "v3", credentials=credentials)

request_body = {
    "snippet": {
        "title": TOPIC,
        "description": "철학이 인류에 주는 선한 영향력 프로젝트",
        "tags": ["철학", "인문학", "자기계발"],
        "categoryId": "22"
    },
    "status": {
        "privacyStatus": "private"
    }
}

media = MediaFileUpload("final_video.mp4")

request = youtube.videos().insert(
    part="snippet,status",
    body=request_body,
    media_body=media
)

response = request.execute()
print("업로드 완료!")
