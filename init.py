
import http.client
import os
import requests
import subprocess
import time
import consul_kv
import pwd, grp
import re

def install_software():
  subprocess.run(["pip3", "install", "--upgrade", "pip"])
  time.sleep(5)
  subprocess.run(["service", "supervisor", "start"])

def add_cronjobs():
  conn = consul_kv.Connection(endpoint="http://consul:8500/v1/")
  target_path_env = "proposal-tool-v2-db/config/ENVIRONMENT"
  target_path_platform = "proposal-tool-v2-db/config/PLATFORM"
  try:
    raw_env = conn.get(target_path_env)
    raw_platform = conn.get(target_path_platform)
  except:
    print("problem connecting to consul...ignoring")
    return None
  regex_string = "^proposal-tool-v2-db/config/"
  for k,v in raw_env.items():
    env = re.sub(regex_string, '', v)
  for k,v in raw_platform.items():
    platform = re.sub(regex_string, '', v)
  cronjob_home_s3_sync = "*/3 * * * * aws s3 sync /home s3://proposal-tool-v2-db-{0}-{1}".format(env, platform)
  cmd0 = "echo \"{}\" >> /var/spool/cron/crontabs/admin".format(cronjob_home_s3_sync)
  p = subprocess.Popen(cmd0, shell=True)
  cronjob_rl_data_s3_sync = "*/4 * * * * aws s3 sync /rl/data s3://proposal-tool-v2-db-{0}-{1}".format(env, platform)
  cmd1 = "echo \"{}\" >> /var/spool/cron/crontabs/admin".format(cronjob_rl_data_s3_sync)
  p = subprocess.Popen(cmd1, shell=True)

  subprocess.run(["chgrp", "crontab", "/var/spool/cron/crontabs/admin"])
  os.waitpid(p.pid, 0)
  time.sleep(10)
  subprocess.run(["service", "cron", "restart"])


def create_admin_user():
  # get admin user password from consul
  conn = consul_kv.Connection(endpoint="http://consul:8500/v1/")
  target_path = "proposal-tool-v2-db/config/admin"
  try:
    admin = conn.get(target_path)
  except:
    print("problem connecting to consul...ignoring")
    return None
  for raw_username, raw_password in admin.items():
    regex_string = "^proposal-tool-v2-db/config/"
    username = re.sub(regex_string, '', raw_username)
    password = raw_password
    homedir = "/home/{}".format(username)
    subprocess.run(["useradd", "-c", "gecos", "-d", "/tmp/admin", "-N", "-p", password, username])
    time.sleep(3)
    print("update admin password")
    subprocess.run(["usermod", "-p", password, username])

def maintain_config_state():
  print("validating operating environment")

def add_user(allusers):
  for raw_username, raw_password in allusers.items():
    # strip the prefix off allusers/raw_username
    regex_string = "^proposal-tool-v2-db/users/"
    username = re.sub(regex_string, '', raw_username)
    password = raw_password
    homedir = "/home/{}".format(username)
    subprocess.run(["useradd", "-c", "gecos", "-d", homedir, "-g", "sftp_users", "-m", "-N", "-p", password, username])
    time.sleep(3)
    subprocess.run(["usermod", "-p", password, username])
    time.sleep(3)
    subprocess.run(["chown", "root", homedir])

def remove_user(user):
  print("removing user: ", user)

def compare_user_list(allusers):
  print("comparing users in consul to passwd")

def is_consul_up():
  url = "http://consul:8500/v1/catalog/service/media-team-devops-automation-jenkins-agent"
  try:
    response = requests.get(url)
  except:
    print("problem checking if consul is up...ignoring")
    return None
  return response.status_code

def scrape_consul_for_users():
  try:
    conn = consul_kv.Connection(endpoint="http://consul:8500/v1/")
    target_path = "proposal-tool-v2-db/users"
    allusers = conn.get(target_path, recurse=True)
    return allusers
  except:
    print("problem scraping consul for users...ignoring")
    return None

def main():
  while True:
    print("main loop")
    maintain_config_state()
    if is_consul_up() == 200:
      print("consul is up")
    else:
      print("consul is down")
    time.sleep(60)

if __name__ == '__main__':
  install_software()
  #create_admin_user()
  #add_cronjobs()
  main()
