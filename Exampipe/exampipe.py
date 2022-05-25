import enum
import json
from multiprocessing.sharedctypes import Value
import os
from time import time
from get_info import extract_info

# From (https://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string)
def find_nth(src, ele, n):
    start = src.find(ele)
    while start >= 0 and n > 1:
        start = src.find(ele, start+len(ele))
        n -= 1
    return start

# Extract key, url, and value from boa script output line
# $key[url] = value$
def extract_url(line):
    ob_pos = line.find('[')
    cb_pos = line.find(']')
    eq_pos = line.find('=')

    if ob_pos == -1 or cb_pos == -1 or eq_pos == -1:
        raise ValueError('Malformed line')
    
    url = line[ob_pos+1:cb_pos]
    ins_pos = find_nth(url,'/', 5)

    if ins_pos == -1:
        raise ValueError('Malformed line')

    key = line[0:ob_pos]
    url = url[0:ins_pos+1] + "tree/master/" + url[ins_pos+1:]
    value = line[eq_pos+2:]
    return (key, url, value)

def main():
    input_json_dir = "input_json"
    input_boa_dir = "input_boa"
    output_json_dir = "output_json"

    url_data_map = {}
    url_timestamp_map = {}
    for filename in os.listdir(os.path.join(os.getcwd(), input_boa_dir)):
        with open(os.path.join(os.getcwd(), input_boa_dir, filename), 'r') as f:
            data = f.read().split('\n')
            for s in data:
                try:
                    key, url, value = extract_url(s)
                    if key == "pj":
                        url_timestamp_map[url] = value
                        url_data_map[url] = {"timestamp" : value}
                except ValueError:
                    print("Boa output could not be decoded")

    for filename in os.listdir(os.path.join(os.getcwd(), input_json_dir)):
        with open(os.path.join(os.getcwd(), input_json_dir, filename)) as f:
            try:
                data = json.load(f)
                for idx, obj in enumerate(data):
                    if obj["url"] in url_data_map:
                        github_api_data = extract_info(obj["url"])
                        github_api_data.update(url_data_map[obj["url"]])
                        data[idx].update(github_api_data)

                with open(os.path.join(os.getcwd(), output_json_dir, filename), 'w+') as fo:
                    json.dump(data, fo)        
                        
            except json.decoder.JSONDecodeError:
                print("JSON cannot be decoded " + filename)

if __name__ == "__main__":
    main()