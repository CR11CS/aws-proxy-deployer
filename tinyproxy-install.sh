sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get upgrade -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install tinyproxy -y
sudo echo "#Specify valid TinyProxy configurations in here. It's recommended not to alter this file unless you're absolutely sure you know what you're doing.
User tinyproxy
Group tinyproxy
Port 8888
Timeout 600
PidFile \"/run/tinyproxy/tinyproxy.pid\"
DefaultErrorFile \"/usr/share/tinyproxy/default.html\"
StatFile \"/usr/share/tinyproxy/stats.html\"
LogLevel Info
MaxClients 100
DisableViaHeader Yes" | sudo DEBIAN_FRONTEND=noninteractive tee /etc/tinyproxy/tinyproxy.conf
sudo systemctl restart tinyproxy.service