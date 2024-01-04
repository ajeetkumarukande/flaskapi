# app.py

from flask import Flask, render_template, request
import spacy
from spacy.lang.en.stop_words import STOP_WORDS
from heapq import nlargest
from urllib.request import urlopen
from bs4 import BeautifulSoup

nlp = spacy.load("en_core_web_sm")
app = Flask(__name__)

def txt_summarizer(raw_docx):
    stopwords = list(STOP_WORDS)
    raw_text = raw_docx
    docx = nlp(raw_text)

    word_frequency = {}
    for word in docx:
        if word.text not in stopwords:
            if word.text not in word_frequency.keys():
                word_frequency[word.text] = 1
            else:
                word_frequency[word.text] += 1
    maximum_frequncy = max(word_frequency.values())
    for word in word_frequency.keys():
        word_frequency[word] = (word_frequency[word]/maximum_frequncy)

    sentence_list = [sentence for sentence in docx.sents]

    sentence_scores = {}
    for sent in sentence_list:
        for word in sent:
            if word.text.lower() in word_frequency.keys():
                if len(sent.text.split(' ')) < 30:
                    if sent not in sentence_scores.keys():
                        sentence_scores[sent] = word_frequency[word.text.lower()]
                    else:
                        sentence_scores[sent] += word_frequency[word.text.lower()]

    summarized_sentences = nlargest(7, sentence_scores, key=sentence_scores.get)
    final_sentences = [w.text for w in summarized_sentences]
    summary = ' '.join(final_sentences)

    return summary

def readingT(mytext):
    total_words = len([token.text for token in nlp(mytext)])
    estimatedTime = total_words / 200.0
    return estimatedTime

@app.route('/', methods=['GET', 'POST'])
def index():
    summary = None
    reading_time = None

    if request.method == 'POST':
        if 'input_text' in request.form:
            text_input = request.form['input_text']
            summary = txt_summarizer(text_input)
            reading_time = readingT(text_input)
        elif 'input_url' in request.form:
            url_input = request.form['input_url']
            try:
                content = urlopen(url_input).read().decode('utf-8')
                summary = txt_summarizer(content)
                reading_time = readingT(content)
            except Exception as e:
                print(f"Error fetching URL content: {e}")

    return render_template('index.html', summary=summary, reading_time=reading_time)

@app.route('/process', methods=['POST'])
def process():
    # Process the form submission for text input
    summary = None
    reading_time = None

    if 'input_text' in request.form:
        text_input = request.form['input_text']
        summary = txt_summarizer(text_input)
        reading_time = readingT(text_input)

    return render_template('index.html', summary=summary, reading_time=reading_time)



@app.route('/process_url', methods=['POST'])
def process_url():
    # Process the form submission for document link input
    summary = None
    reading_time = None

    if 'input_url' in request.form:
        url_input = request.form['input_url']
        try:
            content = urlopen(url_input).read().decode('utf-8')
            summary = txt_summarizer(content)
            reading_time = readingT(content)
        except Exception as e:
            print(f"Error fetching URL content: {e}")

    return render_template('index.html', summary=summary, reading_time=reading_time)


if __name__ == '__main__':
    app.run(debug=True)
