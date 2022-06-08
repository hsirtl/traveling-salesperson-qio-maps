
from flask import Flask,render_template
import logging
logging.basicConfig(level=logging.DEBUG)


app = Flask(__name__)
app.logger.setLevel(logging.DEBUG)

@app.route('/')
def map_func():
	return render_template('bing_map.html')
if __name__ == '__main__':
    app.run(debug = True) 