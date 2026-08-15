from pathlib import Path
from urllib.parse import urlparse
import json

# filter out useless messages
def classify(msg_content: str):
    # filter our messages with just a url (likely gifs)
    try:
        result = urlparse(msg_content)
        if result.scheme and result.netloc:
            return "junk"
    except ValueError:
        pass
    
    if len(msg_content) < 5:
        return "junk"
    
    return "valid"

# grab only needed parts from the data
# returns message authors' data and all parsed messages
def parse_msgs(msgs):
    # open raw json file
    with open(msgs, "r", encoding='utf-8') as f:
        msgs_data = json.loads(f.read()).get('messages')
        
    identifiers = {}
    counter = 0
    parsed_msgs = []
    
    for msg in msgs_data:
        # remove whitespace and junk
        content = msg.get('content').strip().replace("\n", " ").replace("\r", " ")
        if not content:
            continue
        if classify(content) == "junk":
            continue
        
        author = msg.get('author')
        if author.get('isBot') == True:
            continue
        
        user_id = author.get('id')
        # if theres no instance of the author in 'identifiers' then add one
        if user_id not in identifiers:
            identifiers[user_id] = {'id': counter, 'usernames': []}
            counter += 1
        
        # check for associated names of ids
        username = author.get('name')
        nickname = author.get('nickname')
        if username not in identifiers.get(user_id).get('usernames'):
            identifiers.get(user_id).get('usernames').append(username)
        if nickname and nickname not in identifiers.get(user_id).get('usernames'):
            identifiers.get(user_id).get('usernames').append(nickname)
        
        insert = {'author_id': identifiers[user_id].get('id'), 'content': content, 'timestamp': msg.get('timestamp')}
        
        parsed_msgs.append(insert)
    
    return parsed_msgs, identifiers
    