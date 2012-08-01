sshfs -o idmap=user stackops@192.168.10.29:/home/stackops/stackops-agent /var/lib/stackops
ln -s /var/lib/stackops/scripts/etc/init/stackops.conf /etc/init/stackops.conf
initctl reload-configuration
