import re

args = '2020-2022'
sub = re.sub(r'(\d{4})','\\1年', args)
print(sub)
isMatch = re.findall(r'(\d{4}年)', sub)
print(isMatch)

