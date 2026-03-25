#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define STRING_LENGTH 300

const char *flag = "dctf{wow_you_are_smart}";

int number_of_questions = 100;

typedef struct {
	char *question;
	char *a;
	char *b;
	char *c;
	char *d;
	char *solution;
} Question;

int rng(int seed)
{
	srand(time(NULL) + seed);
	int random = rand();
	return random;
}

FILE *open_file(char *name)
{
	FILE *fp = fopen(name, "r");
	if (fp == NULL) {
		printf("File \"%s\" does not exist!", name);
		return NULL;
	}
	return fp;
}

void fill_questions(Question **questions)
{
	FILE *question_fp = open_file("question.txt");
	FILE *solution_fp = open_file("solution.txt");
	FILE *abcd = open_file("choice.txt");

	for (int i = 0; i < number_of_questions; i++) {
		char *str_question = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));
		char *str_solution = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));
		char *A = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));
		char *B = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));
		char *C = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));
		char *D = (char *) malloc((STRING_LENGTH + 1) * sizeof(char));

		fgets(str_question, STRING_LENGTH + 1, question_fp);
		fgets(str_solution, STRING_LENGTH + 1, solution_fp);

		fgets(A, STRING_LENGTH + 1, abcd);
		fgets(B, STRING_LENGTH + 1, abcd);
		fgets(C, STRING_LENGTH + 1, abcd);
		fgets(D, STRING_LENGTH + 1, abcd);

		questions[i]->question = str_question;
		questions[i]->solution = str_solution;
		questions[i]->a = A;
		questions[i]->b = B;
		questions[i]->c = C;
		questions[i]->d = D;
	}

	fclose(question_fp);
	fclose(solution_fp);
	fclose(abcd);
}

int main()
{
	int num_questions = 20;
	char user_answer[STRING_LENGTH];

	// classic setup
        setvbuf(stdin, 0, _IONBF, 0);
        setvbuf(stdout, 0, _IONBF, 0);
        setvbuf(stderr, 0, _IONBF, 0);

	// create
	int *chosen_questions = (int *) calloc(number_of_questions, sizeof(int));
	Question **questions = (Question **) malloc(number_of_questions * sizeof(Question *));
	for (int i = 0; i < number_of_questions; i++)
		questions[i] = (Question *) malloc(sizeof(Question));
	fill_questions(questions);

	for (int i = 0; i < num_questions; i++) {
		int nr = rng(i*num_questions) % number_of_questions;
		if (!chosen_questions[nr]) {
			chosen_questions[nr] = 1;
		}
		else {
			int m = 0;
			while (chosen_questions[(nr+m)%number_of_questions]) {
				m++;
			}
			chosen_questions[(nr+m)%number_of_questions] = 1;
		}
	}
	int *questions_for_game = (int *) malloc(num_questions * sizeof(int));
	int m = 0;

	for (int i = 0; i < number_of_questions; i++) {
		if (chosen_questions[i]) {
			questions_for_game[m] = i;
			m++;
		}

	}
	// game loop
	int points = 0;
	for (int i = 0; i < num_questions; i++) {
		int current = questions_for_game[i];
		printf("Question: %d/%d\n\n", 1+i, num_questions);
		printf("%d. %s", current+1, questions[current]->question);
		printf("	A. %s", questions[current]->a);
		printf("	B. %s", questions[current]->b);
		printf("	C. %s", questions[current]->c);
		printf("	D. %s\n", questions[current]->d);
		printf("Answer: ");
		// user input 
		fgets(user_answer, STRING_LENGTH, stdin);
		if (!strncmp(user_answer, questions[current]->solution, 1)) {
			points++;
			printf(user_answer);
			printf(" is correct!\n");
		}
		else {
			printf("Wrong, correct answer was %s", questions[current]->solution);
		}
		// correct?
		printf("------------------------------------------\n");
	}
	printf("Points: %d/%d\n", points, num_questions);

	// cleanup
	free(questions_for_game);
	for (int i = 0; i < number_of_questions; i++) {
		free(questions[i]->question);
		free(questions[i]->solution);
		free(questions[i]->a);
		free(questions[i]->b);
		free(questions[i]->c);
		free(questions[i]->d);
		free(questions[i]);
	}
	free(questions);
	free(chosen_questions);
	return 0;
}
