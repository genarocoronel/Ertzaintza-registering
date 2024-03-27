DB_URL="https://kv.replit.com/v0/eyJhbGciOiJIUzUxMiIsImlzcyI6ImNvbm1hbiIsImtpZCI6InByb2Q6MSIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJjb25tYW4iLCJleHAiOjE3MTE2MTE1MTUsImlhdCI6MTcxMTQ5OTkxNSwiZGF0YWJhc2VfaWQiOiJjOGQ5M2FiNC1mMGUxLTQwMTktOTVhMS00ZDZiNDUxZGMyMjAiLCJ1c2VyIjoiR2VuYXJvQ29yb25lbCIsInNsdWciOiJFcnR6YWludHphLXJlZ2lzdGVyaW5nIn0.CUKCkN5wZBS0B_71Ed-vZeefl-bRVSK0lgV_coOZQ5PcjIofXNmT_HOsrf1qQv--izSB4Owu6RT0mUyu7S5W0g"
import requests
import json

def get_keys():
    rg = requests.get(DB_URL+"?prefix=")
    rgjs = rg.text.split("\n")
    return rgjs


def get_key(key):
    rg = requests.get(DB_URL+"/"+key)
    rgjs = rg.json()
    return rgjs

def grab_values():
    keys = get_keys()
    valuesdict = {}
    for key in keys:
        valuesdict[key] = get_key(key)
    json.dump(valuesdict, open("outputs/valuesdict.json", "w"))


def save_distinct_values(distinct_values):
    json.dump(list(distinct_values), open("outputs/distinct_values.json", "w"))


def restore_values():
    valuesdict = json.load(open("outputs/valuesdict.json"))
    return valuesdict


if __name__ == "__main__":
    valuesdict = restore_values()
    stag = set()
    for (key, value) in valuesdict.items():
        tgk = tuple(value)
        stag.add(tgk)
    print(len(valuesdict), len(stag))
    save_distinct_values(stag)
