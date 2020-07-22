string = '['
for i in range(24):
	string += '[' + str(i) + ', 0, 0], '
	if i == 23:
		string = string[:-2] + ']'
		print(string)