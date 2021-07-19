import re
from http.server import HTTPServer, BaseHTTPRequestHandler
import requests
import json


sourceSiteURL = "https://streamani.net/loadserver.php?id="
webServerPort = 4321

def get_response(id):
    response = requests.get(sourceSiteURL + id)
    html = response.text
    return html

def find_value(html, key, num_chars=2, separator='"'):
    pos_begin = html.find(key) + len(key) + num_chars
    pos_end = html.find(separator, pos_begin)
    return html[pos_begin: pos_end]

def get_link(id):
    html = get_response(id)
    cleaned_str = find_value(html, 'sources:[', 0, ']').replace('file','"file"').replace('label', '"label"').replace("'", '"')
    data = json.loads(cleaned_str)
    return data['file']

class Redirect(BaseHTTPRequestHandler):
	def do_GET(self):
		try:
			linkId = str(self.path)
			linkId = linkId.replace("/?id=","")
			linkId = linkId.replace("/?=","")
			
			print("gtting " + linkId)
			print(linkId)
			if not re.match("^[A-Za-z0-9=_-]*$", linkId):
				# this id is invalid
				self.send_response(200)
				self.send_header("Content-type", "text/html")
				self.end_headers()
				
				self.wfile.write(b"<body>id is invalid</body>")
				self.wfile.close()
				self.wfile.flush()
			else:
				# get download link
				sourceUrl = get_link(linkId)
				print(sourceUrl)
				if sourceUrl == "":
					self.send_response(200)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					
					self.wfile.write(b"<body>could not find this anime</body>")
					self.wfile.close()
					self.wfile.flush()
				else:
					# redirect user
					# self.send_response(302)
					# self.send_header('Location', sourceUrl)
					# self.end_headers()
					
					self.send_response(200)
					self.send_header("Content-type", "text/html")
					self.end_headers()
					
					self.wfile.write(sourceUrl.encode("utf-8"))
					self.wfile.close()
					self.wfile.flush()
		except Exception as e:
			print(e)

try:
	print("----------- bot started ---------")
	HTTPServer(("", int(webServerPort)), Redirect).serve_forever()
except Exception as e:
	print(e)

