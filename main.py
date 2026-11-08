from pathlib import Path
from dotenv import set_key
from openai import OpenAI
import parser, chunker, db, argparse, os, sys, classifier

def main():
    arg_parser = argparse.ArgumentParser()
    sub = arg_parser.add_subparsers(dest='command', required=True)

    parse_cmd = sub.add_parser('parse', help='Parse a chat export into the database')
    parse_cmd.add_argument("filepath", type=new_path, help='Path to the export.json file')
    
    cls_cmd = sub.add_parser('classify', aliases='cls', help='Parse a chat export into the database')
    cls_cmd.add_mutually_exclusive_group(required=True)
    cls_cmd.add_argument('--k', help='Set LLM API')
    cls_cmd.add_argument('--r', help='Classify parsed messages')
    
    view_cmd = sub.add_parser('view', help='View results')
    
    args = arg_parser.parse_args()

    # the user uses the parse command alongside their export.json file
    if args.command == 'parse':
        parse_msgs(args.filepath)
        
    if args.command in ('classify', 'cls'):
        if args.k:
            set_api()
        elif args.r:
            classify_msgs()

# Behavior: checks whether the entry is a valid file path
# Return: returns a Path object
# Parameters:
# - entry: a string containing the user input
def new_path(entry):
    file_path = Path(entry)
    
    if not file_path.exists:
        raise argparse.ArgumentTypeError(f"invalid file")
    
    return file_path

# Behavior: parses messages and stores them in sqlite3 db
# Parameters:
# - path: the path to the chat export file
def parse_msgs(path: Path):
    db.init_db()
    
    msgs, authors = parser.parse_msgs(path)
    
    db.insert_authors(authors)
    db.insert_messages(msgs)
    
    rows = db.get_all_messages()
    assignments = chunker.chunk_msgs(rows)

    db.set_chunk_ids(assignments)
    
def classify_msgs():
    classifier.classify_msgs()
    
def set_api():
    base_url = input("enter api base url, ex: https://api.openai.com/v1: ")
    api_key = input("enter api key: ")
    model_name = input("enter model name, ex: gemini-1.5-pro: ")
    
    if (test_api(base_url, api_key, model_name)):
        set_key('.env', 'BASE_URL', base_url)
        set_key('.env', 'API_KEY', api_key)
        set_key('.env', 'MODEL_NAME', model_name)

# Behavior: sends a test request to the provided api
# Returns:
# - boolean: True if model successfully responds, False if an error occurs
# Parameters:
# - base_url: base url of the open-ai compatible provider
# - api_key: user api key
# - model_name: ai model to send request to
def test_api(base_url, api_key, model_name):
    client = OpenAI(
        base_url=base_url,
        api_key=api_key,
    )
    
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": "Respond with 'OK'"}],
        )
        print("model responded with '" + response.choices[0].message.content)
        return True
    except OpenAI.AuthenticationError:
        print('invalid API key', file=sys.stderr)
    except OpenAI.NotFoundError:
        print('invalid base URL / model', file=sys.stderr)
    except OpenAI.RateLimitError:
        print('rate limited', file=sys.stderr)
    except OpenAI.APIConnectionError:
        print('could not connect', file=sys.stderr)
    except OpenAI.APIError as e:
        print(f"API error: {e}", file=sys.stderr)
    
    return False
    
if __name__ == '__main__':
    main()