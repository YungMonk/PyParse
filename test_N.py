args = {'name': 'y'}
print(args)
args.clear()
print(args)
if isinstance(args, (dict,)):
    print('yes')
