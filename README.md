## mongo-slowms
Analyze cluster wide mongo slow queries using 10gen’s mtools and send report in CSV format to respective team members.
It can be used for standalone mongo instance and for replica sets.

#prerequisite
- python, python-pip, mtools, fabric 

# Installation 
```
yum install python python-pip
pip install mtools
pip install fabric
```

# Scripts used 
- mongofab.py, mongoslowlog.py

#Setup 
- Add your mongo instance/Replica set details to ``env.roledefs`` in mongofab.py file like below.
    - mongofab.py
```
      env.roledefs = {
          'PP': { 'hosts' : ['X.X.X.X'], 'rname' : 'PP' },
          'PROD1': { 'hosts' : ['X.X.X.X', 'X.X.X.X'], 'rname' : 'PROD1' },
          'PROD2': { 'hosts' : ['X.X.X.X','X.X.X.X','X.X.X.X'], 'rname' : 'PROD2' },
      }
```
- And change SMTP server’s setting in ``mongoslowlog.py`` according to your environment.
  - mongoslowlog.py

    ```
    MailFrom = devops@gmail.com
    Server = "X.X.X.X"  # SMTP server's IP
    ```
```
``mongoslowlog.py --help``
Usage: mongoslowlog.py [options] arguments

Options:
  -h, --help            show this help message and exit
  -f MONGOSLOWLOG, --file=MONGOSLOWLOG
                        File name/path to parse and send slow log report
  -d DATABASE, --database=DATABASE
                        database name for which report needs to be generated
                        or all as default value
  -c COUNT, --count=COUNT
                        # of slow query or 20 by default
  -i EMAIL, --email=EMAIL
                        First Email-ID
  -j EMAIL1, --email1=EMAIL1
                        Second Email-ID
```

- Now setup Crontab for both the scripts.
    - You need to change the ``PROD1`` in both the below crons with ``instance name`` that you have defined in ``mongofab.py`` file.

```
1 0 * * * fab -R PROD1 -f /custom-scripts/slowlog/mongofab.py  getdata
10 0 * * * python /custom-scripts/slowlog/mongoslowlog.py -f /tmp/PROD1/mongo-all.log -c 100 -i ops1@gmail.com -j dev1@gmail.com -d test
```

# Output 
![alt tag](https://raw.github.com/sauravyadav/mongo-slowms/blob/master/output.png)

