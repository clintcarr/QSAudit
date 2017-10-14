# QSAudit
__Summary__

QSAudit is a tool that ingests information from the Qlik Sense Repository APIS and creates a Word Document as an Output.  The information captured is the owner of objects (both applications and objects within the application).  This information can then be used to determine who has created content.

__Usage__

From PowerShell execute .\create_QSAudit.exe --help

QSAudit supports connecting to the QRS via certificates with the --certs switch or Windows Authentication with the --user and --password switches.

__Example__

![Alt Text](https://github.com/clintcarr/QSAudit/raw/master/images/qsAudit.gif)
