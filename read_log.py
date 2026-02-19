import sys

try:
    with open('backend/test_email_log_2.txt', 'r', encoding='utf-16') as f:
        print(f.read())
except Exception as e:
    print(f"Error reading utf-16: {e}")
    try:
        with open('backend/test_email_log_2.txt', 'r', encoding='utf-8') as f:
            print(f.read())
    except Exception as e2:
        print(f"Error reading utf-8: {e2}")
        with open('backend/test_email_log_2.txt', 'rb') as f:
            print(f.read())
