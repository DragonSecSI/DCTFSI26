## App

A web renderer for a custom markup language. Basically markdown with different syntax. Math is rendered with LaTeX (Tectonic) and code is highlighted via Pygments.

## Vulnerability

LaTeX allows you to read and write text files, but since the flag is in env and /proc/self/environ contains null bytes (so not a valid text file), you have to get a bit more creative. Pygments is written in Python, so you can overwrite some of the Pygments source files using LaTeX in order to get code execution and dump the flag (with built-in exfil, since rendered code is returned to the user).

## Steps to Solve

1. Run the Docker container.
2. Set the URL in the `./solv.py` script.
4. Run it.
5. The flag is printed to the console.
