# bamboo-docker-automated

Docker Image and Python script to automagically start a Bamboo instance inside Docker

# Requirements

* Docker
* Ansible
* Python 2.7
* Python Library: Requests

# How-To

1) Run quickstart.sh

OR

1) Install the virtual environment
    * ansible-playbook devenv-playbook.yml
2) Build the docker image for bamboo
    * docker build bamboo/. -t bamboo
3) Run the Docker Container
    * docker run --name bamboo -e CONTEXT_PATH=ROOT -p 8085:8085 bamboo
4) Place your bamboo key next to the script file
    * file name should be "bambookey_modified"
    * Make sure it is in the proper format, there are some formatting issues with this file.  There should be slashes in the key itself
5) Run the script
    * v/bin/python scripts/forms.py
    * you should see a number of print lines while it is working, expect to see
        * waiting for response
        * Illegal Exception while OSGI is down, waiting
        * Timeout waiting for OSGI, waiting
    * Once everything has run, you should see: build complete


# Details

 * The docker container itself was lifted from "descoped/bamboo" but updated to the latest bamboo version.  Updating the line in the file to the latest version number should get you a later bamboo, but I cannot guarantee the script will work
 * The virtual environment / playbook / Ansible / requirements text files are all optional.  You can just install requests directly to your python if you'd like, but I find this easier and more stable for reproduction
  