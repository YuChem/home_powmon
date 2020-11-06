# home_powmon
Home power monitor project

### Unit tests

    python -m unittest discover -s tests -p *.py
    
## Raspberry PI installation
Install minimal CLI raspbian.

Install Docker

    curl -sSL https://get.docker.com | sh
    sudo usermod -aG docker pi
    sudo reboot

Install git

    sudo apt-get install git

checkout this repo

    git clone https://github.com/YuChem/home_powmon
    
build docker images

    sudo apt-get -y install python3-pip libffi-dev libssl-dev
    sudo pip3 install docker-compose
    
start system

    docker-compose up 
