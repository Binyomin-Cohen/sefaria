from flask import Flask, request, send_file
from sefaria_explorer import get_words, context_words, word_cloud
app = Flask(__name__)

@app.route('/chacham', methods=["POST"])
def get_image():
    return word_cloud(chacham)