# Enumeration

As always, the first step is to scan the machine's ports.

![](./assets/ports.png)

On the website, I found a robots.txt file containing an endpoint to an administrator login form.

![](./assets/robots.png)

![](./assets/administrator_login.png)

# CMS version number
Searching for configuration files, I discovered that Joomla's configuration endpoint is located at `/administrator/manifests/files/joomla.xml`.

![](./assets/joomla.png)

To identify the full version number, I looked at this and guessed this was the latest version:

![](./assets/updates_mysql.png)

# SQLI

With this, I had an email address `admin@joomla.org` and a version number. Searching for CVEs on joomla, I found this one https://www.exploit-db.com/exploits/42033 and tested it:

![](./assets/sqli_test.png)

It worked! The exploit even includes the syntax to run sqlmap, so I used the tool to dump the db. After a while, I retrieved a password hash `$2y$10$0veO/JSFh4389Lluc4Xya.dfy2MF.bZhz0jVMw.V.d3p12kBtZutm` with the username `jonah`.

![](./assets/jonah.png)

![](./assets/jonah_hash.png)

I used Hashcat to crack the hash and recovered the password: `spiderman123`. I tried using these credentials to log in via SSH, but it didn’t work. However, I could access the administrator panel.

![](./assets/administrator_panel.png)

There was on the administrator panel a template editor where it is possible to write php code. I used this to upload a php reverse shell.

![](./assets/administrator_template.png)

After executing the reverse shell, I gained access and stabilized my shell.

# User flag

Inspecting at the configuration.php file, I found credentials for the root user. I tested them but they didn't work. However, there was a second user on this machine, `jjameson`, maybe the credentials could work for him ?

![](./assets/configuration.png)

![](./assets/etc_passwd.png)

![](./assets/jjameson.png)

# Root flag

The next step was to check if I could execute commands with `sudo` without providing a password. Most of the time, this is not as easy but in this case, it worked.

![](./assets/sudo_perms.png)

So, yum can be used. But how ? From https://gtfobins.github.io/gtfobins/yum/ I saw that I could spawn a shell with this command. In order to do that, I needed to run the following commands:

```bash
TF=$(mktemp -d)
cat >$TF/x<<EOF
[main]
plugins=1
pluginpath=$TF
pluginconfpath=$TF
EOF

cat >$TF/y.conf<<EOF
[main]
enabled=1
EOF

cat >$TF/y.py<<EOF
import os
import yum
from yum.plugins import PluginYumExit, TYPE_CORE, TYPE_INTERACTIVE
requires_api_version='2.1'
def init_hook(conduit):
  os.execl('/bin/sh','/bin/sh')
EOF

sudo yum -c $TF/x --enableplugin=y
```

Basically, what it does is create a plugin that runs a shell with the permissions of the runner. Since, I've used sudo I became root.

![](./assets/sudo.png)
