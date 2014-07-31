Apache Flask Configuration
====
Source: [article](https://beagle.whoi.edu/redmine/projects/ibt/wiki/Deploying_Flask_Apps_with_Apache_and_Mod_WSGI)

Project Structure
========
* pgeo
    * docs
    * examples
    * pgeo
    * test

Apache Configuration
========
Edit file /etc/apache2/ports.conf 
```script
<VirtualHost *:80>
	ServerName guido
	WSGIDaemonProcess flaskapp user=kalimaha group=kalimaha threads=5
	WSGIScriptAlias /demo/pgeo /var/www/public_html/wsgi/demo_pgeo.wsgi
	WSGIScriptAlias /dev/pgeo /var/www/public_html/wsgi/dev_pgeo.wsgi
	<Directory /var/www/public_html/http/demo/pgeo>
		WSGIProcessGroup flaskapp
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>
	<Directory /var/www/public_html/http/dev/pgeo>
		WSGIProcessGroup flaskapp
		WSGIApplicationGroup %{GLOBAL}
		Order deny,allow
		Allow from all
	</Directory>
</VirtualHost>
```

WSGI Configuration
========
Create file *demo_pgeo.wsgi* in the */var/www/public_html/wsgi* folder
```python
import sys
sys.path.insert(0,'/home/kalimaha/Development/git-repositories/Geobricks/pgeo')
from pgeo.rest import app as application
```