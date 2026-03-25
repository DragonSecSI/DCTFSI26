#!/usr/bin/env python3
import os

FLAG: str = os.environ.get("FLAG", "dctf{FLAAAAAAAAAAAAG}")

class Formatter:
    def format_box(self, width: str) -> str:
        middle: str = f"| Your age: {{self.age:{width}}} |".format(self=self)
        total_len: int = len(middle)

        return (
            total_len * "-" +
            "\n" + middle + "\n" +
            total_len * "-"
        )

    def ask(self) -> None:
        self.age: str = input("How old are you? ")
        self.width: str = input("How wide do you want the nice box to be? ")

    def run(self) -> None:
        while True:
            self.ask()
            print(self.format_box(self.width))

Formatter().run()
