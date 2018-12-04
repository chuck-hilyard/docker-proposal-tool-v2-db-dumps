
#import http.client
import os
#import requests
import subprocess
import time
#import consul_kv
#import pwd, grp
#import re
import datetime


def take_dump():
  MONGO_INITDB_ROOT_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
  MONGO_INITDB_ROOT_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']
  datestring = datetime.datetime.today().strftime('%Y-%m-%d-%H%M')
  environment = os.environ['environment']
  platform = os.environ['platform']
  target_host = "proposal-tool-v2-db.media.{}.{}.reachlocalservices.com".format(environment, platform)
  target_dir = "/data/backups/{}".format(datestring)
  subprocess.run(["mongodump", "-u", MONGO_INITDB_ROOT_USERNAME, "-p", MONGO_INITDB_ROOT_PASSWORD, "-h", target_host, "-o", target_dir])


def main():
  while True:
    print("main loop")
    take_dump()
    time.sleep(3600)

if __name__ == '__main__':
  main()
