Apache Flask Configuration
====
Source: [article](https://beagle.whoi.edu/redmine/projects/ibt/wiki/Deploying_Flask_Apps_with_Apache_and_Mod_WSGI)
Apache Configuration
========
Edit file /etc/apache2/ports.conf 
```script
<VirtualHost *:80>
    ServerName localhost
    WSGIDaemonProcess flaskapp user=kalimaha group=kalimaha threads=5
    WSGIScriptAlias /flasktest1 /var/www/public_html/wsgi/flasktest1.wsgi
    <Directory /var/www/project_name/http/flasktest1>
        WSGIProcessGroup flaskapp
        WSGIApplicationGroup %{GLOBAL}
        Order deny,allow
        Allow from all
    </Directory>
</VirtualHost>
```
