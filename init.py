# environment variables are set via terraform

import os
import subprocess
import time
import datetime


def take_dump():
  print("mongodump")
  MONGO_INITDB_ROOT_USERNAME = os.environ['MONGO_INITDB_ROOT_USERNAME']
  MONGO_INITDB_ROOT_PASSWORD = os.environ['MONGO_INITDB_ROOT_PASSWORD']
  datestring = datetime.datetime.today().strftime('%Y-%m-%d-%H%M')
  environment = os.environ['environment']
  platform = os.environ['platform']
  target_host = "proposal-tool-v2-db.media.{}.{}.reachlocalservices.com".format(environment, platform)
  target_dir = "/data/backups/{}".format(datestring)
  subprocess.run(["mongodump", "-u", MONGO_INITDB_ROOT_USERNAME, "-p", MONGO_INITDB_ROOT_PASSWORD, "-h", target_host, "-o", target_dir])

def sync_dumps_to_s3():
  print("syncing to s3")
  target_bucket = "s3://proposal-tool-v2-db-{}-{}/backups".format(os.environ['environment'], os.environ['platform'])
  subprocess.run(["aws", "s3", "sync", "/data/backups", target_bucket])

def cleanup_local_dumps():
  print("removing old dumps")
  try:
    folders = os.listdir(path='/data/backups')
    print("FOLDERS:",  folders)
  except FileNotFoundError as e:
    print("exception {}".format(e))

def main():
  while True:
    print("main loop")
    cleanup_local_dumps()
    take_dump()
    time.sleep(2)
    sync_dumps_to_s3()
    print("sleeping for 2 hours")
    time.sleep(3600)

if __name__ == '__main__':
  main()
