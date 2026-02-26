import json
def test_json(s):
    try:
        json.loads(s)
        print(f"Success for {repr(s)}")
    except Exception as e:
        print(f"Error for {repr(s)}: {repr(e)}")

test_json('1 {"token": "abc"}')
test_json('0a')
test_json('""a')
test_json("'{\"token\": \"abc\"}'")
test_json('"{')
