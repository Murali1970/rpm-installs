#!/usr/bin/python

# Import necessary modules 
import sys
import os
import paramiko
import getpass

# set the log file location 
paramiko.util.log_to_file("filename.log")

def ssh_to_server(hostname, username, directory):

   ssh = paramiko.SSHClient()
   ssh.load_system_host_keys()
   ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

   print hostname, username 

   private_key = paramiko.RSAKey.from_private_key_file ("/var/lib/jenkins/.ssh/id_rsa")

   ssh.connect(hostname, username=username, password='', key_filename = private_key)

   sftp = ssh.open_sftp()
  
   # print list of RPM files to be uploaded and installed 
   for listoffiles in os.walk(directory):
      print "list of RPM files = " , listoffiles[2]

   # sftp the RPM files    
   for file in listoffiles[2]:
      sftp.put(directory + "/" + file, "/tmp/" + file)

   # execute a sample command 
   stdin, stdout, stderr = ssh.exec_command("uptime")
   print stdout.readlines()

   # Get the package name which is the RPM file without the extension 
   packagename = file[:len(file) - 4]
   print "packagename", packagename
   
   stdin, stdout, stderr = ssh.exec_command('rpm -qa | grep ' + packagename)
   if stdout == packagename:
      print "package already installed"
   else: 
      # execute command to install RPM
      stdin, stdout, stderr = ssh.exec_command("sudo rpm -ivh " + "/tmp/" + file)
      print stdout.readlines()
      print stderr.readlines()

def trigger_run(): 

   # Enforce rules 
   if len (sys.argv) < 2:
      print "You must set the directory of RPMs"
      sys.exit(-1)
   else:
      directory = sys.argv[1]; 
      print directory;

   # At least one hostname must be specified 
   if len (sys.argv) < 3:
      print "You must specify at least one hostname to install RPMs"
      sys.exit(-1)

   j = 2

   while j < len(sys.argv):  
   
      server=sys.argv[j]
      [username, hostname] =  apply_rules (server)
      ssh_to_server(hostname, username, directory)
      j=j+1

def apply_rules (server):
  
   info = []

   username = "jenkins" 
   hostname = server         
 
   info.insert(0,hostname)
   info.insert(0,username)
   return info 


trigger_run()


