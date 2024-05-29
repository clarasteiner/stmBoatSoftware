import pexpect
from pexpect import popen_spawn
import getpass

ssh = popen_spawn.PopenSpawn('ssh cisco@192.168.100.1')
print(ssh)
