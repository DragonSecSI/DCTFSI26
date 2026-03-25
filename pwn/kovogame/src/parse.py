import csv

# input all.csv
infile = 'all.csv'

# output question.txt (one question per line)
out_question = 'question.txt'
# output solution.txt (one solution per line)
out_solution = 'solution.txt'
# output choice.txt (option per line - 4 per question)
out_choice = 'choice.txt'

with open(out_question, 'w', encoding='utf-8') as file:
    pass
with open(out_solution, 'w', encoding='utf-8') as file:
    pass
with open(out_choice, 'w', encoding='utf-8') as file:
    pass

with open('all.csv', mode='r', encoding='utf-8') as file:
	reader = csv.reader(file)
	# Skip the header row if necessary
	header = next(reader)

	questions = open(out_question, 'a')
	solution = open(out_solution, 'a')
	choice = open(out_choice, 'a')

	for row in reader:
		questions.write(row[0] + '\n')
		choice.write(row[1] + '\n' + row[2] + '\n' + row[3] + '\n' + row[4] + '\n')
		solution.write(row[5] + '\n')

	questions.close()
	solution.close()
	choice.close()

