#!/usr/bin/python

import enum
import math
from genericpath import exists
from time import time
import sys
import json
from multiprocessing.sharedctypes import Value
import os
import math
from time import time
from tracemalloc import start
from get_info import extract_info
from dotenv import load_dotenv

# From (https://stackoverflow.com/questions/1883980/find-the-nth-occurrence-of-substring-in-a-string)
# def find_nth(src, ele, n):
#     start = src.find(ele)
#     while start >= 0 and n > 1:
#         start = src.find(ele, start+len(ele))
#         n -= 1
#     return start

# Extract key, url, and value from boa script output line
# $key[url] = value$
def extract_url(line):
    ob_pos = line.find('[')
    cb_pos = line.find(']')
    eq_pos = line.find('=')

    if ob_pos == -1 or cb_pos == -1 or eq_pos == -1:
        raise ValueError('Malformed line')
    
    url = line[ob_pos+1:cb_pos]
    # ins_pos = find_nth(url,'/', 5)

    # if ins_pos == -1:
    #     raise ValueError('Malformed line')

    key = line[0:ob_pos]
    # url = url[0:ins_pos+1] + "tree/master/" + url[ins_pos+1:]
    value = line[eq_pos+2:]
    return (key, url, value)

def process_api(input_filename, output_filename, input_boa_dir, output_json_dir, input_json_dir, start_idx, max_api_calls, cur_idx):
    url_data_map = {}
    with open(os.path.join(os.getcwd(), input_boa_dir, input_filename), 'r') as f:
        data = f.read().split('\n')
        data.pop()
        for s in data:
            try:
                key, url, value = extract_url(s)
                if key == "pj":
                    url_data_map[url] = {"timestamp" : int(value) / 1000000}
            except ValueError as e:
                print("Boa output could not be decoded: " + str(e))
    
    if not os.path.exists(os.path.join(os.getcwd(), output_json_dir)):
        os.makedirs(os.path.join(os.getcwd(), output_json_dir))
        print("Create directory: " + str(os.path.join(os.getcwd(), output_json_dir)))

    with open(os.path.join(os.getcwd(), input_json_dir, output_filename)) as f:
        try:
            data = json.load(f)
            for idx, obj in enumerate(data):
                if obj["url"] in url_data_map:
                    github_api_data = extract_info(obj["url"])

                    stars_forks = (math.log(max(1.0, float(github_api_data["num_stars"]))) + \
                                   math.log(max(1.0, float(github_api_data["num_forks"]))))
                    open_closed_issues = max(1.0, float(github_api_data["num_closed_issues"]) - float(github_api_data["num_open_issues"])) / \
                                        (max(1.0, float(github_api_data["num_contributors"])))
                    try:
                        timestamp_metric = ((time() - float(url_data_map[obj["url"]]["timestamp"])) / float(360*24))**(-math.log(1.14))
                        ranking_metric = (stars_forks + open_closed_issues)**timestamp_metric
                    except:
                        ranking_metric = sys.float_info.max

                    ranking_metric = math.log(max(1.0, ranking_metric))
                    print(ranking_metric)
                    url_data_map[obj["url"]]["ranking_metric"] = ranking_metric

                    cur_idx += 1
                    github_api_data.update(url_data_map[obj["url"]])
                    data[idx].update(github_api_data)
                    if cur_idx >= start_idx + max_api_calls:
                        print("Max API calls reached")
                        return

            with open(os.path.join(os.getcwd(), output_json_dir, output_filename), 'w+') as fo:
                json.dump(data, fo)        
                        
        except json.decoder.JSONDecodeError:
            print("JSON cannot be decoded " + output_filename)

def main():
    if len(sys.argv) < 3:
        print("Argument should be: python3 exampipe.py <start_idx> <max_api_calls>")
        return

    try:
        start_idx = int(sys.argv[1])
        max_api_calls = int(sys.argv[2])
        cur_idx = start_idx
    except:
        print("<start_idx> and <max_api_calls> should be int: python3 exampipe.py <start_idx> <max_api_calls>")
        return

    input_json_dir = "input_json"
    input_boa_dir = "input_boa"
    output_json_dir = "output_json"

    if len(sys.argv) == 5:
        input_filename = str(sys.argv[3])
        output_filename = str(sys.argv[4])
        process_api(input_filename, output_filename, input_boa_dir, output_json_dir, input_json_dir, start_idx, max_api_calls, cur_idx)
        return

    url_data_map = {}
    for filename in os.listdir(os.path.join(os.getcwd(), input_boa_dir)):
        with open(os.path.join(os.getcwd(), input_boa_dir, filename), 'r') as f:
            data = f.read().split('\n')
            data.pop()
            for s in data:
                try:
                    key, url, value = extract_url(s)
                    if key == "pj":
                        url_data_map[url] = {"timestamp" : float(value) / 1000000}
                except ValueError as e:
                    print("Boa output could not be decoded: " + str(e))

    if not os.path.exists(os.path.join(os.getcwd(), output_json_dir)):
        os.makedirs(os.path.join(os.getcwd(), output_json_dir))
        print("Create directory: " + str(os.path.join(os.getcwd(), output_json_dir)))

    for filename in os.listdir(os.path.join(os.getcwd(), input_json_dir)):
        with open(os.path.join(os.getcwd(), input_json_dir, filename)) as f:
            try:
                data = json.load(f)
                for idx, obj in enumerate(data):
                    if obj["url"] in url_data_map:
                        # curl -H "Authorization: token api_key" -X GET https://api.github.com/rate_limit 
                        github_api_data = extract_info(obj["url"])
                        
                        stars_forks = (math.log(max(1.0, float(github_api_data["num_stars"]))) + math.log(max(1.0, float(github_api_data["num_forks"]))))
                        open_closed_issues = max(1.0, float(github_api_data["num_closed_issues"]) - float(github_api_data["num_open_issues"])) / (max(1.0, float(github_api_data["num_contributors"])))
                        try:
                            timestamp_metric = ((time() - float(url_data_map[obj["url"]]["timestamp"])) / float(360*24))**(-math.log(0.9))
                            ranking_metric = (stars_forks + open_closed_issues)**timestamp_metric
                        except:
                            ranking_metric = sys.float_info.max

                        ranking_metric = math.log(max(1.0, ranking_metric))
                        print(ranking_metric)
                        url_data_map[obj["url"]]["ranking_metric"] = ranking_metric

                        cur_idx += 1
                        github_api_data.update(url_data_map[obj["url"]])
                        data[idx].update(github_api_data)
                        if cur_idx >= start_idx + max_api_calls:
                            print("Max API calls reached")
                            return

                with open(os.path.join(os.getcwd(), output_json_dir, filename), 'w+') as fo:
                    json.dump(data, fo)        
                        
            except json.decoder.JSONDecodeError:
                print("JSON cannot be decoded " + filename)

if __name__ == "__main__":
    load_dotenv()
    api_key = os.getenv('GITHUB_PERSONAL_ACCESS_TOKEN')
    main()