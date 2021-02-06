# MASAPT 🤖 ↔ &#129302; ↔ 🤖
# <hr>

<br>

_❗_ <span style="color:red">_Warning_</span>


> This tool is developed for academic and research purposes as a part of the
  _Multiagent systems_ course at _Faculty of organization and informatics_.
  This tool is not to be used without consent of a second party whose security
  is being tested.
>
> Author holds no responsibility for any damage made with this tool and
  condemns any nefarious usage of the same.

<hr>

## Welcome to...

_Multi-Agent System for Automated Penetration Testing_ 🐱‍💻


![usage_gif](readme_files/run.gif)

<br>

### Explore → Exploit → Report → 📝

A system of autonomous agents communication over XMPP to coordinate and perform
penetration testing. In a CLI tool!

Just pass the URL, wait a bit, then read the report!

![report1](readme_files/report1.png)
![report1](readme_files/report2.png)


<hr>

### How to run?

_Difficult_.


**Install requirements**

There's a fair number of prerequisites and requirements to install:

* Kali Linux 2020.4 (_optional_)
* Python 3.8
* Pip3
* SQLMap (Already installed on Kali)
* Nmap (Already installed on Kali)


Beside Python and pentesting tools that can be found on Kali, you also need
access to some XMPP service. For testing the system I used **ejabberd**
running locally.

To run the agents on your XMPP server of choice, you will need to create
the following users. You can of course create other users, but then you
will need to pass the new JID and PWD parameters when creating agents in
_masapt_ script.

| JID | PASSWORD |
| :--:| :------: |
| _repoter@domain_ | repoterSecret |
| _explorer@domain_ | explorerSecret |
| _coordinator@domain_ | coordinatorSecret |
| _sqlinjector@domain_ | injectorSecret |


**Setup:**

After the prerequisites have been installed and XMPP has been set up:

1. cd into the project folder
```bash
    cd ../MASAPT
```

2. Add directory to PATH
```bash
    export PATH=$PATH:/path/to/MASAPT
    source ~/.bashrc
```

3. Install python requirements
```Python
    pip install -r requirements.txt
```
4. Make _masapt_ script executable
```bash
    chmod +x masapt
```

**Run:**

Start the system with:
```bash
    masapt -t url/to/target
```

<br>
<hr>

### Further work

**More agents:**

- [ ] Dos agent
- [ ] XSS agent
- [ ] Buffer overflow agent

**Expand _Explorer.py_ so it can:**
- [ ] Run Harvester
- [ ] Run more OSINT tools

<hr>

## System overview 🔎

## Theory dive 📜


## References 🔗

[1] Big thanks to **_Audi-1_** and his excellent [SQLI labs](https://github.com/Audi-1/sqli-labs)
for testing error based, blind boolean and time based SQL injection!

[2] [Chu, Ge, and Alexei Lisitsa. "Agent-based (BDI) modeling for automation of penetration testing." arXiv preprint arXiv:1908.06970 (2019).](https://arxiv.org/abs/1908.06970)

[3] [Qiu, X., Wang, S., Jia, Q., Xia, C., & Xia, Q. (2014, October). An automated method of penetration testing. In 2014 IEEE Computers, Communications and IT Applications Conference (pp. 211-216). IEEE.](https://ieeexplore.ieee.org/abstract/document/7017198)
