# server.py

from flask import Flask, request, send_file, jsonify, render_template_string
from gevent.pywsgi import WSGIServer
from dotenv import load_dotenv
import os

from tts_handler import generate_speech, get_models, get_voices
from utils import require_api_key, AUDIO_FORMAT_MIME_TYPES

app = Flask(__name__)
load_dotenv()

API_KEY = os.getenv('API_KEY', 'your_api_key_here')
PORT = int(os.getenv('PORT', 5050))

DEFAULT_VOICE = os.getenv('DEFAULT_VOICE', 'en-US-AndrewNeural')
DEFAULT_RESPONSE_FORMAT = os.getenv('DEFAULT_RESPONSE_FORMAT', 'mp3')
DEFAULT_SPEED = float(os.getenv('DEFAULT_SPEED', 1.0))

# DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'tts-1')

# 添加一个简单的 HTML 模板
HOME_TEMPLATE = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OpenAI通用的微软Edge TTS API</title>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; padding: 20px; max-width: 800px; margin: 0 auto; }
        h1 { color: #333; }
        pre { background-color: #f4f4f4; padding: 10px; border-radius: 5px; }
    </style>
</head>
<body>
    <h1>OpenAI通用的微软Edge TTS API</h1>
    <p>这是一个基于 Edge TTS 的 OpenAI TTS API 替代品。</p>
    <h2>API 端点：</h2>
    <ul>
        <li>TTS 生成：<code>/v1/audio/speech</code> (POST)</li>
        <li>列出模型：<code>/v1/models</code> (GET/POST)</li>
        <li>列出语音：<code>/v1/voices</code> (GET/POST)</li>
        <li>列出所有语音：<code>/v1/voices/all</code> (GET/POST)</li>
    </ul>
    <h2>使用示例：</h2>
    <pre>
    <p>
    <a href="https://www.youtube.com/@all.ai.">视频教程</a>
    <a href="https://github.com/aigem/edgeTTS-openai-api">更多信息请参考项目说明</a></p>
    </pre>
</body>
</html>
"""

@app.route('/')
def home():
    return render_template_string(HOME_TEMPLATE, port=PORT)

@app.route('/v1/audio/speech', methods=['POST'])
@require_api_key
def text_to_speech():
    data = request.json
    if not data or 'input' not in data:
        return jsonify({"error": "Missing 'input' in request body"}), 400

    text = data.get('input')
    # model = data.get('model', DEFAULT_MODEL)
    voice = data.get('voice', DEFAULT_VOICE)

    response_format = data.get('response_format', DEFAULT_RESPONSE_FORMAT)
    speed = float(data.get('speed', DEFAULT_SPEED))
    rate = data.get('rate', None)
    volume = data.get('volume', None)
    pitch = data.get('pitch', None)
    proxy = data.get('proxy', None)
    mime_type = AUDIO_FORMAT_MIME_TYPES.get(response_format, "audio/mpeg")

    # Generate the audio file in the specified format with speed adjustment
    output_file_path = generate_speech(text, voice, response_format, speed, rate, volume, pitch, proxy)

    # Return the file with the correct MIME type
    return send_file(output_file_path, mimetype=mime_type, as_attachment=True, download_name=f"speech.{response_format}")

@app.route('/v1/models', methods=['GET', 'POST'])
@require_api_key
def list_models():
    return jsonify({"data": get_models()})

@app.route('/v1/voices', methods=['GET', 'POST'])
@require_api_key
def list_voices():
    specific_language = None

    data = request.args if request.method == 'GET' else request.json
    if data and ('language' in data or 'locale' in data):
        specific_language = data.get('language') if 'language' in data else data.get('locale')

    return jsonify({"voices": get_voices(specific_language)})

@app.route('/v1/voices/all', methods=['GET', 'POST'])
@require_api_key
def list_all_voices():
    return jsonify({"voices": get_voices('all')})

print(f" Edge TTS (Free Azure TTS) Replacement for OpenAI's TTS API")
print(f" ")
print(f" * Serving OpenAI Edge TTS")
print(f" * Server running on http://localhost:{PORT}")
print(f" * TTS Endpoint: http://localhost:{PORT}/v1/audio/speech")
print(f" ")

if __name__ == '__main__':
    http_server = WSGIServer(('0.0.0.0', PORT), app)
    http_server.serve_forever()
