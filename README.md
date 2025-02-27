The full documentation of QLines, including app+proxy+blog is available in Google doc: 
https://docs.google.com/document/d/1RpFBwtAG9uG10FQ6VcyiW-3TbMRWepAfR2PxorEg0Eo/edit#


Main road-map for qlines
MVP by myself, including all GUI stuff and so on => Start monetisation => hire GUI guy => More marketing by conservative actions => Hire sales and expand marketing => enjoy!

A package with easier deployment for simple IoT devices. Current IoT providers need development but the idea is to make life easier for the customers. This is the value we are selling.
The idea is to be on shoulders of Giants and avoid developing stuff from scratch
The idea is to monetize from beginning
Could be expanded to Android/IOS apps later.
Could be expanded to home security stuff later.
Having consultation besides the main product is missed by bigger providers now.
Good price compared to big providers
Start with LoraWAN after basic MVP started
Thingsborad and JFrog are my models to get inspired on which features I should develop next

Architecture and redundancy
qlines_app
qlines_proxy
qlines_blog

The architecture doesn’t use any DNS fail-over. It’s complicated and not reliable however it seems new browsers (and clients) are capable of switching it.
Both domains ‘www.qlines.net’ and ‘blog.qlines.net’ are resolved to same IP address (217.61.104.75 as of 2.4.2023)
3 docker containers are in a single machine now. Think about upgrading machine. Later I will expand to multiple VMs for better availability. Now the goal is to make it easy to reproduce by docker-compose in case of failure.
I need clear instructions for:
Reproduce the apps, proxy, blog, etc.
Quick restore of DBs in case of crash or VM wipe out

































Site
VM function
CPU (vcpu)
Mem (GB)
Disk (GB)
Description
Geo site 1
LB+Proxy
2
2
100


Geo site 1
App1
4
8
200
Each could handle all load
Geo site 1
App2
4
8
200
Each could handle all load
Geo site 1
App3
4
8
200
Each could handle all load
Geo site 1
DB1
8
16
500














Geo site 2
LB+Proxy
2
2
100


Geo site 2
App1
4
8
200
Each could handle all load
Geo site 2
App2
4
8
200
Each could handle all load
Geo site 2
App3
4
8
200
Each could handle all load
Geo site 2
DB2
8
16
500














Geo site 3
DB3
8


500









The application is running on 2 sites and DB on 3 sites
The 3 sites must in same city, not far from each other with good QoS for DB sync
Need to make sure that I have diverse VMs. For e.g., the networking issue inside the docker engine is a common problem. For the moment, it’s easier to manage it through multiple VMS. Remember the case when blog.qlines.net was not possible to launch (in Jul 2023).


Problems still to be solved in above schematic:
The sync between dbs is not clear
The switch-over between DBs is not clear
The redundancy of LB is not provided


Architecturre for MVP
2 VM with 40G disk, 2 cores, 4G mem
Each including proxy, blog, app, db, etc., exactly same. The proxy in each routes the traffic between two for maintenance and upgrade purposes
DNS could also route from VM1 to VM2 if needed


		




Important processes
QLINES_APP
Redis
RQWorker
Kafka / Zookeeper
QLines / Gunicorn
MongoDB
ClickHouse
QLINES_BLOG
MySQL
NGINX
To-be-completed

QLINES_PROXY
NGINX
To-be-completed

Running multiple services in one container
Each Docker container is supposed to carry only one process/service. This is understandable. But for MVP purpose, and making the product easy to launch and manage, we need to run multiple daemons in one container, even DBs! I realised that current init scripts could be run properly with —priviledged flag enabled. Current docker-compose doesn’t have this (previously I had it). Now I guess if I run it with priviledged enabled in docker-compose, I can convert all systemd to init script. I know init script is older than systemd but at least this is a good temporary solution to keep the Mac dev env without struggling to switch to VM or remote Linux env.
Also some important points are discussed here: https://docs.docker.com/config/containers/multi-service_container/


How is the “device overview” table rendered?

The main backend file is “qlines.py”
Hitting the route “/devices” renders the template “dash_devices.html”
The “device_overview_table.js” is executed and sends the request to the backend at “/api/data”
The route “/api/data” is the main core of data fetch. The idea is to:
Fetch data from ClickHouse
Verify it with Mongo to make sure that it is registered. Drop the unregistered devices.
Log/Alert/Report to admin about unregistered devices.

Device’s page interactions
The data with associated user ID is pushed to Kafka and SocketIO under the Flask sends it to the client’s browser.
These scripts are important for this interaction:
websocket_updates.js
chart1.js
Method of ‘background_thread’ in the ‘qlines.py’
Removed the socketio with this commit: https://github.com/mehdiabolfathi/qlines_app/commit/4d22373f5f5b056ce7983a0a6b0a00a13f22f226

Now all the data is being updated by the polling every 1sec here:
chart1.js
dash_device_single.html
SocketIO
Refer to docs about Miguel’s SocketIO. I use this in my Flask application. It needs eventlet (check gunicorn command) to run together with Flask and Gunicorn.
gunicorn --worker-class eventlet -w 1 qlines:app --bind 0.0.0.0:5000
gunicorn is needed to enable the websocket. The websocket works only with eventlet. Check documentation for details which are saved in the notes ‘Websocket ‘ in the iNotes/Mac
The socket backend is in the main file qlines.py
gunicorn is needed to enable the websocket. The websocket works only with eventlet. Check documentation for details.
make sure to install the exact version. The evetlet 0.30.2 is necessary here. If not mentioned, the conflict happens
Installation on Mac (as Dev env)
Edit /etc/hosts and add the entries to point to the container on Mac.

Installation on Production
Preparation of the VPS
After the VPS is requested, it might be necessary to upgrade the OS to the latest Debian:
apt-get --allow-releaseinfo-change update
Upgrade the Debian 10 to 11: https://www.cyberciti.biz/faq/update-upgrade-debian-10-to-debian-11-bullseye/
Upgrade the Debian 11 to 12: https://www.cyberciti.biz/faq/update-upgrade-debian-11-to-debian-12-bookworm/


After the new VPS is upgraded, install the following:
apt-get update;apt-get install git vim tmux

Add the Mac SSH public key into the VPS:
Vi ~/.ssh/authorized_keys
Copy your Mac public key to this file
Add the VPS SSH to the GitHub
In VPS, run ssh-keygen


Then update the ~/.bashrc with the following new lines:

alias plt="docker exec -it $(docker ps  | grep 'qlines_app' | awk '{print $1}') /bin/bash"
alias p="ps -ef | egrep 'apache|sql|mongo|python'"
alias s='netstat -tulpen | grep ssh'
alias pip=pip3
alias ql='cd /opt/qlines_app'
alias teh='ssh -p 2277 root@localhost'
alias muc='ssh -p 2266 root@localhost'
alias dps='docker ps -a --format="table {{.ID}}\t{{.Image}}\t{{.Command}}\t{{.Status}}\t{{.Names}}"'
alias tmux_start='tmux new-session -t res -d;tmux new-session -t log -d;tmux new-session -t mqtt -d;tmux new-session -t mongo -d;tmux new-session -t client -d;tmux new-session -t test -d;'

Installation of Docker engine
install docker engine on the production linux server. Ref: https://docs.docker.com/engine/install/debian/, start from the step "Set up the repository"
Run ‘docker network create qlines’ to create the necessary network for all containers


Installation of the QLines app
cd /opt/
git clone git@github.com:mehdiabolfathi/qlines_app.git
cd /opt/qlines_app
Clean up all the docker cash and images if needed by “docker system prune -a”
docker compose up -d
Logout and login again
Enter ‘plt’ and you should enter the qlines container.
Enter ‘p’ inside the container to see the processes’ status.
Vi ~/.bashrc and edit PS1 to show PROD in the prompt
Logout and login to enable the bashrc
Clean up the docker unused images with: “docker system prune”
Installation of the QLines blog
The blog is built initially inspired by this guide: https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-docker-compose In this doc, I try reuse the above structure and to summarise the steps to build a proxy in front of multiple apps (main app + blog).

Make sure to run this on a machine that maps to the domain which is now 'blog.qlines.net'


cd /opt/
git clone git@github.com:mehdiabolfathi/qlines_blog.git
cd qlines_blog


Vi .env, fill these info there:
MYSQL_ROOT_PASSWORD=dfi_65gh
MYSQL_USER=xuserx
MYSQL_PASSWORD=jeGrgbk2




if the blog is created fresh, connect to mysql and create the DBs first:
Docker exec -it 2ce51f03503f /bin/bash
mysql -uroot -p  (pass: dfi_65gh)
CREATE DATABASE IF NOT EXISTS `wordpress_qlines`;
CREATE DATABASE IF NOT EXISTS `wordpress_bigbang`;
GRANT ALL PRIVILEGES ON wordpress_bigbang.* TO 'xuserx'@'%' WITH GRANT OPTION;
GRANT ALL PRIVILEGES ON wordpress_qlines.* TO 'xuserx'@'%' WITH GRANT OPTION;
(good ref: https://medium.com/@sam.moulem/two-wordpress-sites-with-docker-eae355fd1b0d)


Then run:
docker compose up -d


Installation of the QLines proxy
cd /opt/
git clone git@github.com:mehdiabolfathi/qlines_proxy.git
Make sure that qlines_app and qlines_blog are already up
Use the “Remote SSH” feature of “VSCode” for easier remote editing the docker-compose.yml and also NGINX configuration files.


In the folder /opt/qlines_proxy, there are two nginx config files. First we need to let certbot to connect to port 80 and we need a minimal nginx config file.


Cd /opt/qlines_proxy
Cp nginx_http.conf ./nginx-conf/nginx.conf


Remove the old certificates that might be there, also pushed to Git:
rm -rf certbot-certificates
In the docker-compose.yml, uncomment the section for ‘certbot’, make sure the indentation is same as other items under “services”.
for qlines.net => in 'docker-compose.yml' use '-d qlines.net -d www.qlines.net' run 'docker compose up' (not with -d option, to see the logs)
Make sure that certificate files are produced in folder /opt/qlines_proxy/certbot-certificates/live
Edit the docker-compose.yml and for blog.qlines.net => in 'docker-compose.yml' use '-d blog.qlines.net' run 'docker compose up' (not with -d option, to see the logs)
Make sure that certificate files are produced in folder /opt/qlines_proxy/certbot-certificates/live


After all certificates are produced, we don’t need the certbot anymore. Replace the nginx config file with the one with SSL settings:
Cd /opt/qlines_proxy
Cp nginx_http_and_https.conf ./nginx-conf/nginx.conf
Edit the docker-compose.yml and comment out the certbot section
Run docker compose up -d
Test addresses ‘qlines.net’ and ‘blog.qlines.net’ to verify if the connection is fine.
Clean up the docker unused images with: “docker system prune”
Reboot the vps with ‘reboot’ command to make sure that all the containers and all sites (qlines.net, blog.qlines.net) are up and running.
Renew the server certificates (Letsencrypt)
While installing the qlines_proxy container, the certificates are installed. But to renew it do the following steps:
Connect to vps through vscode
Cd /opt/qlines_proxy/
Edit the docker-compose.yml file and uncomment the part for ‘certbot’ service.
for qlines.net => in 'docker-compose.yml' use '-d qlines.net -d www.qlines.net' 
docker compose up -d
Ignore the warning like: “WARN[0000] a network with name custom_qlines_network exists”
docker compose restart webserver
Make sure that certificate files are produced in folder
/opt/qlines_proxy/certbot-certificates/live
Repeat this for blog.qlines.net
Verify the certificates are renewed by browsing the pages
Comment again the certbot part in the docker-compose.yml file
docker compose up -d
The certbot container must be stopped. Remove it.
Clean up the docker unused images with: “docker system prune”
Done!


TODO later:
The guide in this chapter probably is very amateur one. Make it better!
Make it periodic like cronjob or so.
I guess the image of ‘certbot’ has already some considerations for it. Check it later when free time.


Health-checks and monitoring the platform
As of 30.8.2023, run the script in the main folder of qlines app:
./check_processes_and_ports.py

In healthy situation, it should show this result:

Process 'rqworker' is OK and running
Process 'mongodb' is OK and running
Process 'mosquitto' is OK and running
Process 'clickhouse-server' is OK and running
Process 'clickhouse-watchd' is OK and running
Process 'redis' is OK and running
Process 'kafka' is OK and running
Process 'gunicorn' is OK and running

Port 9092 is open on 0.0.0.0.    Process: kafka
Port 2181 is open on 0.0.0.0.    Process: kafka
Port 7010 is open on 0.0.0.0.    Process: clickhouse
Port 9000 is open on 0.0.0.0.    Process: clickhouse
Port 9004 is open on 0.0.0.0.    Process: clickhouse
Port 9005 is open on 0.0.0.0.    Process: clickhouse
Port 9009 is open on 0.0.0.0.    Process: clickhouse
Port 27017 is open on 127.0.0.1.    Process: mongodb
Port 6379 is open on 127.0.0.1.    Process: redis
Port 5000 is open on 0.0.0.0.    Process: qlines
Port 1883 is open on 127.0.0.1.    Process: mosquitto

Unit-tests and end-to-end tests
To be completed. The idea is to document the tests here to create a good overview.


References and Main Docs
It is possible that most of the documents are in iNotes on Mac. Here is only the selected docs are mentioned.

SocketIO
Socketio, Miguel’s github repo for flask-socketio: https://github.com/miguelgrinberg/Flask-SocketIO
Socketio, Miguel’s documentation: https://flask-socketio.readthedocs.io/en/latest/getting_started.html
General Web Samples
Admin dashboard with flask and django: https://dev.to/sm0ke/admin-dashboard-dattaable-coded-in-two-python-flavors-2bj5

System Design Guide
https://bit.ly/3SuUR0Y

Kafka and Python (Confluent)
https://towardsdatascience.com/how-to-build-a-simple-kafka-producer-and-consumer-with-python-a967769c4742








Appendix 1 - Old qlines_app readme and running based on docker
About current architecture
Apache => WSGI => Flask
Redis is involved for message queue use cases
"Init scripts" are used. So far ok but need to make a better approach for Docker.
Dockerfile will be updated with the configuration steps
For tests (on python packages or OS packages) use current container, the Dockerfile helps to create from scratch later
Using VSCODE in the docker folder in Mac local filesystem, then docker in the VPS
Using aliases inside the container, use aliases outisde the container
Clickhouse and Mosquitto only enabled in lab for the moment, refer to notes to install
Steps to build the environment - both test and prod
install docker engine on the production linux server. Ref: https://docs.docker.com/engine/install/debian/, start from the step "Set up the repository"
in case of Mac, go to the Docker folder of the Mac, probably it is in this folder: /Users/amc/Desktop/G/Docker
git clone git@github.com:mehdifth/platform.git (note: Github must already have the ssh public keys)
rename the platform to "qlines" to be able to use more apps with this platform
mv platform qlines
mkdir platform
mv qlines ./platform/
now there is one platform folder which could include folders like qlines, app1, app2, ...
cd ./platform
docker build -t debian_platform_image_v1 ./qlines/
in dev platform: docker run -d -p80:80 -p443:443 -p 7000-7100:7000-7100 --shm-size 2g --privileged -v "$(pwd)":/opt/ debian_platform_image_v1
in prod platform: docker run -d -p80:80 -p443:443 --restart always --shm-size 2g --privileged -v "$(pwd)":/opt/ debian_platform_image_v1
docker exec -it a5ff9cec9f2e /bin/bash
or use the alias "plt", for this you need to define this alias in mac/host as below:
alias plt="docker exec -it $(docker ps | grep 'debian_platform_image' | awk '{print $1}') /bin/bash"
alias p="ps -ef | egrep 'apache|sql|mongo|python'"
in each host, update the git outside the docker container. This way you will have the SSH key on the Git.
install nodejs manually, follow this: https://www.digitalocean.com/community/tutorials/how-to-install-node-js-on-debian-10, refer to my iNotes for more details
Deployment to production todos
make sure to use latest and same version of docker and docker-compose in Lab and Prod servers
enable the google analytics tag in all html filesystem
Manage the SSL certificate/Letsencrypt As it was not possible to install in docker because of snapd, renew it in the host oustide of the docker container and move the files in /etc/letsencrypt to inside the docker.
Install NGINX outside of the container and use following config in /etc/nginx/sites-enable (no need to link from sites-available):
server { listen 80; listen [::]:80;
   root /var/www/your_domain/html;
    index index.html index.htm index.nginx-debian.html;

    server_name blog.qlines.net qlines.net www.qlines.net;

    location / {
            try_files $uri $uri/ =404;
    }


}
remove all other files in this folder this covers all the 3 domains of "qlines.net", "www.qlines.net" and "blog.qlines.net" then run the "certbot --nginx" outside of the docker container for 3 times stop the nginx outside of the docker copy the /etc/letsencrypt to inside the docker to /etc/letsencrypt restart the nginx inside the docker done!
insdie docker, vi ~/.bashrc => change LAB to PROD in PS1
inside docker, chmod 777 /opt/qlines/mylogs.log
**How the HA is designed VM1:
LB1, Blog1, App1 VM2:
LB2, Blog2, App2 LB1 has a docker container to offload SSL and distribute the load, based on available app servers and subdomains (for blog versus app) LB1 sees all the containers but sends only to 1. If one container fails sends the single one to 2 LB2 sees all the containers, but it is standby
DNS is switching between LB1 and LB2
High traffic will result in spawning the app containers. It means VM1 is big enough for this. DB1 and DB2 are in separate VM servers because of sensitivies. All the nodes see DB1 and DB2 at the same time but send only to one of them. TODO: Need arbiter here!
for MVP, I will go with big VM and backup/restore approach and later will have a sophisticated approach like above or use AWS! for MVP, I will have nginx proxy in front (outside of containers) to SSL offload, route based on subnet (blog or app), etc. Having 2 container behind it. Wordpress blog will use the official image with docker-compose: https://www.hostinger.com/tutorials/run-docker-wordpress
What to remember about Redis and message queue
install the redis-server on both linux and python by "apt-get install redis" and "pip3 install redis"
use this in the main python script where you want to push the jobs to queue:
import redis
from rq import Queue
r = redis.Redis()
q = Queue('app1', connection=r)


create rqworker.py with this content:
#!/usr/bin/env python
import os

import redis
from rq import Worker, Queue, Connection

listen = ['app1']
redis_url = os.getenv('REDISTOGO_URL', 'redis://localhost:6379')
conn = redis.from_url(redis_url)

if __name__ == '__main__':
    with Connection(conn):
        worker = Worker(list(map(Queue, listen)))
        worker.work()



the "rqworker.py" needs to be run always in the background, better to do with init script of systemd
if you want to put into the queue, do like this: result = q.enqueue(yourmethod, inputs_to_the_metho)
"yourmethod" is the method to consume the object in the queue, and "inputs_to_the_metho" is the input for that method. "app1" is the pipe name in the queue.
for more queues, it is enough to expand this list for more items: listen = ['app1']











Appendix 2 - Old qlines_blog readme 
What is this?
The blog is built initially based on this guide: https://www.digitalocean.com/community/tutorials/how-to-install-wordpress-with-docker-compose In this doc, I try reuse the above structure and to summarise the steps to build a proxy in front of multiple apps (main app + blog).
Steps to build the wordpress - summarised what grasped from digitalocrean tutorial
Make sure to run this on a machine that maps to the domain which is now 'blog.qlines.net'
Make sure to remove the volumes in the folder /var/lib/docker/volumes which are related to any old installation.
mkdir qlines_blog
cd qlines_blog
mkdir nginx-conf
vi nginx-conf/nginx.conf:
use the content of 'nginx-conf--before-ssl.conf' and copy it to nginx-conf/nginx.conf
in the main folder (qlines_blog), create '.env' file with this content (values are in Mac notes):
MYSQL_ROOT_PASSWORD=********
MYSQL_USER=********
MYSQL_PASSWORD=********
cat .gitignore
.env


cat .dockerignore
.git
docker-compose.yml
.dockerignore
fill the docker-compose.yml
Make sure to replace '--force-renewal' with '--staging' and remove the '443:443 or use the file 'docker-compose--before-ssl.yml'
Run 'docker-compose up -d'
By running docker-compose, it will create these folders (volumes):
/var/lib/docker/volumes/qlines_blog_certbot-etc
/var/lib/docker/volumes/qlines_blog_dbdata
/var/lib/docker/volumes/qlines_blog_wordpress
'qlines_blog' prefix is the name of the folder that has 'docker-compose.yml'
After running docker-compose, check it with 'docker ps -a'. The certbot container should be exited and other 3 should be up.
check the container logs with 'docker-compose logs container_name'
yet another interesting command: 'docker-compose exec webserver ls -la /etc/letsencrypt/live'
Now that you know your request will be successful, you can edit the certbot service definition to remove the --staging flag and replace it with --force-renewal which will tell Certbot that you want to request a new certificate with the same domains as an existing certificate. or use the file 'docker-compose--after-ssl.yml' and copy to docker-compose.yml
be careful that in this stage to have these configs:
webserver only port 80 (not 443 yet)
to have --force-renewal instead of --staging
run 'docker-compose up --force-recreate --no-deps certbot' You will also include the --no-deps option to tell Compose that it can skip starting the webserver service, since it is already running
Enabling SSL in the Nginx configuration
docker-compose stop webserver
No need to run this line - the file is already in the repo (it's mentioned in the tutorial): curl -sSLo nginx-conf/options-ssl-nginx.conf https://raw.githubusercontent.com/certbot/certbot/master/certbot-nginx/certbot_nginx/_internal/tls_configs/options-ssl-nginx.conf
We need a new nginx config file now:
vi nginx-conf/nginx.conf
copy the content of 'nginx-conf--after-ssl.conf' here
make sure to replace all the parts with 'your_domain' with your domain name
copy the docker-compose--after-ssl.yml to docker-compose.yml
make sure to have --force-renewal (instead of --staging) and port 443 in the docker-compose.yml file.
docker-compose up -d --force-recreate --no-deps webserver
docker-compose ps
The output should indicate that your db, wordpress, and webserver services are running, and certbot is exited.
continue the installation through the web: https://your_domain , for pictures refer to digitalocean's main tutorial
Now we should add the logic to renew the certificate. The file ssh_renew.sh is already in the repo.
chmod +x ssl_renew.sh
crontab -e: ''' 0 12 * * * /opt/platform/qlines_blog/ssl_renew.sh >> /var/log/cron_ssl_renew_qlines_blog.log 2>&1 '''
Steps to build app+blog - after adjustments
todo









Appendix 3 - Old qlines_proxy readme


1) Creating network
Create a network to communicate between containers, even though they are created by different compose files: run 'docker network create qlines'
2) Starting the qlines_app and qlines_blog
Run the qlines_app and qlines_blog and make sure the app is alive and could be reached from NGINX proxy
3) To create the SSL certificates in the beginning when the certificate folder is empty
Warning: If you already have the certificate and would like to renew, skip this section check 'nginx_http.conf' to make sure that your domain is correct cp nginx_http.conf ./nginx-conf/ check the folder nginx-conf to make sure that correct file is there
check 'docker-compose.yml' to make sure that your domain is correct
for qlines.net => in 'docker-compose.yml' use '-d qlines.net -d www.qlines.net' run 'docker-compose up'
for blog.qlines.net => in 'docker-compose.yml' use '-d blog.qlines.net' run 'docker-compose up'
repeat this for each domain. Be careful that 'qlines.net' and 'www.qlines.net' could be done together.
stop the nginx and certbot containers.
now it is expected that your certificates are created
in 'docker-compose.yml' comment out the section for the service 'certbot'
in the folder 'nginx-conf', replace the 'nginx_http.conf' with 'nginx_http_and_https.conf' and run the 'docker-compose up' again
4) To build the apps/blogs on top of the existing certificates
This is for the situation when the certificates are already created and now you want to connect other apps to the NGINX Proxy through SSL ports only. In the folder 'nginx-conf', use the configuration 'nginx_http_and_https.conf' instead of the 'nginx_http.conf' Run 'docker-compose up'
5) To renew the certificates - IT_IS_A_TODO
in the folder of qlines_proxy, edit the docker-compose.yml and uncomment the certbot part. in the host's command line, outside of containers, run: 'docker-compose run certbot renew'
it will create the images and containers and runs the renewal command I haven't tried the full renewal yet. Make sure it works properly and update this readme section. Stop the certbot container. Remove the certbot container. Put back the comments in docker-compose.yml about the certbot's section.


