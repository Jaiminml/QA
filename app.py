from distutils.log import debug
import os
from flask import Flask, render_template
import requests
from flask import request
from googleapiclient.discovery import build
from pprint import pprint as pp
import math

app = Flask(__name__)


def google_search(search_term, api_key, cse_id, **kwargs):
    service = build("customsearch", "v1", developerKey=api_key)
    
    num_search_results = kwargs['num']
    if num_search_results > 100:
        raise NotImplementedError('Google Custom Search API supports max of 100 results')
    elif num_search_results > 10:
        kwargs['num'] = 10 # this cannot be > 10 in API call 
        calls_to_make = math.ceil(num_search_results / 10)
    else:
        calls_to_make = 1
        
    kwargs['start'] = start_item = 1
    items_to_return = []
    while calls_to_make > 0:
        res = service.cse().list(q=search_term, cx=cse_id, **kwargs).execute()
        items_to_return.extend(res['items'])
        calls_to_make -= 1
        start_item += 10
        kwargs['start'] = start_item
        leftover = num_search_results - start_item + 1
        if 0 < leftover < 10:
            kwargs['num'] = leftover
        
    return items_to_return 


@app.route('/hye', methods=['GET', 'POST'])
def index2():
    if request.method == 'POST':
        form = request.form
        question = form['question']
        print(question,'question')
        api_key = "AIzaSyADiRertMWRLGyo5wpaAZ7lAJlt0Bu1G3Q"
        cse_id = "06ae4119a2a8e4b78"
        NUM_RESULTS = 20
        result = google_search(question,api_key,cse_id,num=NUM_RESULTS)
        
        final_res = []
        
        for i in result:
            try:
                r = requests.post(
                url="https://hf.space/embed/jaimin/Open_Domain_QA/+/api/predict",
                json={
                    "data": [i['snippet'],question]},
                )
                response = r.json()
                print(response,'response')
                final_res.append(response['data'])
            except:
                pass


        return final_res

    return render_template("index.html")


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0',debug=True)



