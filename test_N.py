import re

args = '在职，急换工作'
if re.search(r'在岗|在职|机会', args, re.S|re.I):
    print('yes')
else:
    print('no')
