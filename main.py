from flask import Flask, request, Response
import requests
import os

# allows for debugging
DEBUG=os.getenv('DEBUG', False) 

app = Flask(__name__)


# change this url to remove indicator
@app.route('/b8af860c6c7f78d5cbcaa86c8f11b268cd0c0295')
def health():
    return "OK"


@app.route('/', defaults={'url': ''}, methods=["GET", "POST"])
@app.route('/<path:url>', methods=["GET", "POST"])
def root(url):
    host=os.getenv('DESTINATION')
    timeout = int(os.getenv('TIMEOUT', 20)) # override using TIMEOUT env variable
    path = f'http://{host}/{url}'
    try:
        r = requests.request(request.method, path, params=request.args, stream=True, 
                            headers=dict(request.headers), allow_redirects=False, 
                            data=request.form, timeout=timeout)
        def generate():
            for chunk in r.raw.stream(decode_content=False):
                yield chunk
        out = Response(generate(), headers=dict(r.raw.headers))
        out.status_code = r.status_code
        return out
    except Exception as e:
        # change these responses to remove indicators
        if DEBUG:
            return f'Error: {str(e)}'
        else:
            return 'Error'
    



if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ('PORT', 8080)))
