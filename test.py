class MyException(Exception):
    pass

try:
    raise MyException('error message TEST')
except MyException as e:
    print('test')
    print(str(e))