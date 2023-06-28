import sseclient

messages = sseclient.SSEClient('http://127.0.0.1:5000//listen')

for msg in messages.events():
    pass