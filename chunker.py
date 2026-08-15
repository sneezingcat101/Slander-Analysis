from datetime import datetime

# sort each message into groups by conversations
def chunk_msgs(msgs: list) -> list:
    assignments = []
    group_counter = 0
    prev = None
    
    for msg in msgs:
        cur = datetime.fromisoformat(msg['timestamp'])
        
        if not assignments:
            assignments.append({'id':msg['id'], 'chunk':group_counter})
            prev = datetime.fromisoformat(msg['timestamp'])
            continue
        
        diff = (cur - prev).seconds / 60
        
        # if the new message was sent 20 minutes after the last, its considered a new conversation
        if (diff > 20 or len(assignments[-1]) > 50):
            group_counter += 1
        
        assignments.append({'id':msg['id'], 'chunk':group_counter})
        prev = datetime.fromisoformat(msg['timestamp'])
    
    return assignments
        