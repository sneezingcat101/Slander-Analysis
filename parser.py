from pathlib import Path
from urllib.parse import urlparse
import json

def classify(msg):
    try:
        result = urlparse(msg)
        if result.scheme and result.netloc:
            return "junk"
    except ValueError:
        pass
    return "valid"

def msg_parser(msgs):
    with open(msgs, "r", encoding='utf-8') as f:
        msgs_data = json.loads(f.read()).get('messages')
    authors = {}
    counter = 0
    raw_msgs = []
    
    for msg in msgs_data:
        content = msg.get('content').strip().replace("\n", " ").replace("\r", " ")
        if not content:
            continue
        if classify(content) == "junk":
            continue
        
        author = msg.get('author')
        if author.get('isBot') == True:
            continue
        
        user_id = author.get('id')
        if user_id not in authors:
            authors[user_id] = {'id': counter, 'usernames': []}
            counter += 1
            
        username = author.get('name')
        nickname = author.get('nickname')
        if username not in authors.get(user_id).get('usernames'):
            authors.get(user_id).get('usernames').append(username)
        if nickname not in authors.get(user_id).get('usernames'):
            authors.get(user_id).get('usernames').append(nickname)
        
        raw_msgs.append(str(authors[user_id].get('id')) + ": " + content)
    
    with open('s.txt', 'w', encoding='utf-8') as f:
        json.dump(authors, f, indent=2)
        f.write("\n".join(raw_msgs))

script_dir = Path(__file__).parent

data_file = script_dir / 'ab.json'

msg_parser(data_file)
    