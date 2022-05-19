import enum
import json
import os
from time import time

# From (https://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string)
def find_nth(src, ele, n):
    start = src.find(ele)
    while start >= 0 and n > 1:
        start = src.find(ele, start+len(ele))
        n -= 1
    return start

def main():
    input_json_dir = "input_json"
    input_boa_dir = "input_boa"
    output_json_dir = "output_json"

    url_timestamp_map = {}
    for filename in os.listdir(os.path.join(os.getcwd(), input_boa_dir)):
        with open(os.path.join(os.getcwd(), input_boa_dir, filename), 'r') as f:
            data = f.read().split('\n')
            for s in data:
                if len(s) > 3 and s[0:3] == "pj[":
                    cb_pos = s.find(']')
                    if cb_pos != -1:
                        url = s[3:cb_pos]
                        eq_pos = s.find('=')
                        ins_pos = find_nth(url, '/', 5)
                        if eq_pos != -1 and ins_pos != -1:
                            url = url[0:ins_pos+1] + "tree/master/" + url[ins_pos+1:]
                            timestamp = s[eq_pos+2:]
                            url_timestamp_map[url] = timestamp

    for filename in os.listdir(os.path.join(os.getcwd(), input_json_dir)):
        with open(os.path.join(os.getcwd(), input_json_dir, filename)) as f:
            try:
                data = json.load(f)
                for idx, obj in enumerate(data):
                    if obj["url"] in url_timestamp_map:
                        data[idx]["timestamp"] = url_timestamp_map[obj["url"]]

                with open(os.path.join(os.getcwd(), output_json_dir, filename), 'w+') as fo:
                    json.dump(data, fo)        
                        
            except json.decoder.JSONDecodeError:
                print("JSON cannot be decoded " + filename)

if __name__ == "__main__":
    main()