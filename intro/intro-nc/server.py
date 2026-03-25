import random
import os

print("Welcome to the math quiz! How fast are you?")

for i in range(25):
    a = random.randint(1, 100)
    b = random.randint(1, 100)
    answer = a + b
    user_input = input(f"{a} + {b} = ")
    user_input = user_input.strip()
    try:
        if int(user_input) != answer:
            print("Wrong answer! Good bye.")
            break
    except ValueError:
        print("Invalid input! Good bye.")
        break
else:
    print(os.environ.get("FLAG", "FLAG{fake_flag_for_testing}"))
