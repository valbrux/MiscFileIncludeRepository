from xml.sax.saxutils import escape
import BaseHTTPServer
import requests
import thread
import ssl
import sys
import re
import os

import urllib3
urllib3.disable_warnings()

class MyHandler(BaseHTTPServer.BaseHTTPRequestHandler):
	def do_POST(s):
		data = ''
		content_len = int(s.headers.getheader('content-length', 0))
		post_body = s.rfile.read(content_len)
		s.send_response(200)
		s.send_header("Content-type", "application/soap+xml;charset=UTF-8")
		s.end_headers()
		if "__00omacmd=getuserrightsonly" in post_body:
			data = escape("<SMStatus>0</SMStatus><UserRightsMask>458759</UserRightsMask>")
		if "__00omacmd=getaboutinfo " in post_body:
			data = escape("<ProductVersion>6.0.3</ProductVersion>")
		if data:
			requid = re.findall('>uuid:(.*?)<',post_body)[0]
			s.wfile.write('''<?xml version="1.0" encoding="UTF-8"?>
							<s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsa="http://schemas.xmlsoap.org/ws/2004/08/addressing" xmlns:wsman="http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd" xmlns:n1="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/DCIM_OEM_DataAccessModule">
							  <s:Header>
							    <wsa:To>http://schemas.xmlsoap.org/ws/2004/08/addressing/role/anonymous</wsa:To>
							    <wsa:RelatesTo>uuid:'''+requid+'''</wsa:RelatesTo>
							    <wsa:MessageID>0d70cce2-05b9-45bb-b219-4fb81efba639</wsa:MessageID>
							  </s:Header>
							  <s:Body>
							    <n1:SendCmd_OUTPUT>
							      <n1:ResultCode>0</n1:ResultCode>
							      <n1:ReturnValue>'''+data+'''</n1:ReturnValue>
							    </n1:SendCmd_OUTPUT>
							  </s:Body>
							</s:Envelope>''')

		else:
			s.wfile.write('''<?xml version="1.0" encoding="UTF-8"?><s:Envelope xmlns:s="http://www.w3.org/2003/05/soap-envelope" xmlns:wsmid="http://schemas.dmtf.org/wbem/wsman/identity/1/wsmanidentity.xsd"><s:Header/><s:Body><wsmid:IdentifyResponse><wsmid:ProtocolVersion>http://schemas.dmtf.org/wbem/wsman/1/wsman.xsd</wsmid:ProtocolVersion><wsmid:ProductVendor>Fake Dell Open Manage Server Node</wsmid:ProductVendor><wsmid:ProductVersion>1.0</wsmid:ProductVersion></wsmid:IdentifyResponse></s:Body></s:Envelope>''')

	def log_message(self, format, *args):
		return

def startServer():
	server_class = BaseHTTPServer.HTTPServer
	httpd = httpd = server_class(('0.0.0.0', 8888), MyHandler)
	httpd.socket = ssl.wrap_socket (httpd.socket, certfile='./server.pem', server_side=True)
	httpd.serve_forever()

startServer()
