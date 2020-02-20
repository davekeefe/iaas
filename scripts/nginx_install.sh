echo "Install epel-release"
sudo yum install -y epel-release

echo "Install nginx"
sudo yum install -y nginx
    
echo "Start nginx service"
sudo systemctl start nginx
