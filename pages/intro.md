---
route: intro
title: Intro
draft: false
hidden: false
auth_required: false
---

# Introduction

Welcome to DCTF!
This is a local Slovenian CTF competition organized by DragonSec SI.
On this page you can find some information about how to use the platform and what tools you might need to compete and solve the challenges.

## tldr:

**Flag format**: `dctf{...}` \
**Team size*: max 3 members \
**Connecting to instances**: `ncat --ssl inst-xxxxxxxxxx.tls.vuln.si 443` or with pwntools `remote('inst-xxxxxxxxxx.tls.vuln.si', 443, ssl=True)`

## Platform

The platform is constructed out of two parts.
This page is the first part, which is CTFd, a popular CTF platform used for hosting challenges and managing teams and scoring.
To compete you need to create an account and join a team (max 3 members per team) and when the competition starts you will be able to see the challenges.
Under the [challenges](/challenges) tab you can see the list of challenges, their categories and points.
When you click on a challenge you will be able to download the files for the challenge to set it up locally.

The second part of the platform is the [instancer](/instancer) which is used to run the challenges on the instancer's servers and connect to them remotely.
When you start an instance of a challenge, you will be given the connection details to connect to it.
For web challenges you will be able to copy the url and for pwn challenges you will get the connection string.

## Tools

To compete you may need some of the below described tools.
Depending on the category of the challenge you may need different tools.
They can be roughly categorized as:

**Web**: docker, Burp Suite
**Pwn**: ghidra, pwntools, pwndbg
**Rev**: ghidra, gdb
**Crypto**: sagemath

### Docker

Docker is used to create a consistent environment of the challenges on your end as well as on the instancer.
Linux users can look up the [docker engine installation](https://docs.docker.com/engine/install/) for their distribution.
Windows and Mac users can install [Docker Desktop](https://www.docker.com/products/docker-desktop/).

Each challenge will come with a `Dockerfile`. To build and run the image, you need to run the following commands in the terminal:

```bash
docker build -t <image_name> .
docker run -ti --rm -p <host_port>:<container_port> <image_name>
```

> Replace the <image_name> with whatever name you want, and the <host_port> and <container_port> with the needed port (usually 8000 for web and 1337 for pwn challenges).

### Burp Suite 

Burp Suite is a web application security testing framework.
It can be used to intercept and modify the traffic between your browser and the web application.
You can download it from the [official website](https://portswigger.net/burp/communitydownload).

### Ghidra

Ghidra is a software reverse engineering framework developed by the NSA.
It can be used to analyze and reverse engineer binary files to understand their functionality (rev) and find vulnerabilities (pwn).
You can download it from [their github repository](https://github.com/NationalSecurityAgency/ghidra).

### Pwntools

Pwntools is an exploitation framework for pwn challenges. Debian (and most Debian based distributions) users can install it with the following command:

```bash
apt install python3-pwntools
```

Otherwise you can install it with pip:

```bash
pip install pwntools
```

> You will need a python environment for this command to work, otherwise you can also run it with --break-system-packages.

To test the install you can run the following code in a python file:

```python
from pwn import *
```

Below is a sample pwntools script that shows how to run a local process, a debugger, a remote connection and a remote connection to the instancer:

```python
from pwn import *

# Use one of the following at a time
p = process('./challenge') # Local challenge
p = gdb.debug('./challenge', gdbscript='''
    b *main
''') # Local challenge with debugger
p = remote('localhost', 1337) # Docker challenge
p = remote('inst-xxxxxxxxxx.tls.vuln.si', 443, ssl=True) # Remote challenge on the instancer

# Exploit goes here

p.interactive()
```

### GDB & Pwndbg

To debug the challenges you need to install gdb and pwndbg. Debian (and most Debian based distributions) users can install gdb with the following command:

```bash
apt install gdb
```

The prefered way of running pwndbg is by cloning and installing it from source.
To do that run the following commands:

```bash
git clone https://github.com/pwndbg/pwndbg
cd pwndbg
./setup.sh
```

Verify the installation by running `gdb` and you should see a `pwndbg>` prompt.

### Sagemath

Sagemath is a mathematical version of python that can be used to solve crypto challenges.
It has a lot of built in functions for number theory, algebra, combinatorics and more.
You can download it from the [official website](https://doc.sagemath.org/html/en/installation/index.html) or install it with pip:

```bash
pip install sagemath
```
