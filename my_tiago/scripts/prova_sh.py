#!/usr/bin/env python
import subprocess
import os
import shlex

#
#subprocess.call(["./base_practice_small_office.sh"])

# cmd = "source ~/tiago_public_ws/devel/setup.bash"
# return_value = os.system(cmd)
# cmd = "cd"
# return_value = os.system(cmd)
# cmd = "cd my_ros_ws/src/my_tiago/scripts"
# return_value = os.system(cmd)
# cmd = "./base_practice_small_office.sh"
# return_value = os.system(cmd)

path = os.path.dirname(os.path.abspath(__file__))
print(str(path))

os.system('pwd')
os.system('ls')
os.system('./simple_office_with_people.sh')

#return_value = os.system(". ./.base_practice_small_office.sh")

#subprocess.call('./prova.sh')

#os.system('. ./base_practice_small_office.sh')


#os.system(". " + str(path) + "./.base_practice_small_office.sh")

#subprocess.Popen(['prova.sh'],stdout=subprocess.PIPE,shell=True)
#
# 
# return_value = os.system(cmd) 

# path = os.path.dirname(os.path.abspath(__file__)) + "/base_practice_small_office.sh"
# os.popen('sh' + path)

#command = shlex.split("env -i bash -c 'source prova.sh'")
#proc = subprocess.Popen(command, stdout = subprocess.PIPE,shell=True)
#for line in proc.stdout:
  #(key, _, value) = line.partition("=")
 # os.environ[key] = value
#proc.communicate()




#subprocess.Popen(['prova.sh "var=11; ignore all" /home/ermanno/my_ros_ws/src/my_tiago/scripts'], shell=True, executable="/bin/bash")
