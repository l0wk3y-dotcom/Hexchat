import os
import json

if __name__ == '__main__':
    for i in range(5):
        users=[{
    'username': "krish",
    "password":"123"
    }]
        file_name='log.txt'
        with open(file_name, 'w') as log:
                json.dump(users, log)