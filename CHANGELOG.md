Version 0.2 - Nov 09, 2015
-------------------------------
### Features
- ability to change the name of auth cookie
- target OS specific behaviour
- switch to project instance role context for fabric comands by using WKTIME_INSTANCE_ROLE environment variable
- creation of invoice in full automatic mode on /admin/timesheet/monthlyinvoice/
- 'amount_equivalent' of MonthlyInvoice
- multi user time traking
- timesheet.models.Salary

### Changes
- django csrftoken cookie not used anymore for nginx cookie based access restriction
- related names of 'invoice extra data' objects for Company and User models now is 'iv_data'
- rename property 'times' to 'period' of timesheet.models.SpentTime
- remove signals, move their logic into models save() methods
- now /admin/timesheet/spenttime shows only working times of currently logged user,
  superuser can see all time trackings of all users

### Bug fixes
- typo in 'reload_fronend' -> reload_fron(T)end
- missed local_settings.py, path for it in .gitignore
- hidden 'workers' on  admin/timesheet/spenttime/ for admin, admin might see/change they
- 'filename' option of reports and invoices should be in read only mode
- error during creation of invoice for worker which does not have filled invoice extra data


Version 0.1 - Sept 26, 2015
-------------------------------
### Features
- add fabric

### Changes
- add nginx cookie based site restrictions
- new project structure, folders: src, logs, backups, py3
- new config file, which contains parameters for project deploy/update: config.ini
- move whole project into separate system account

### Bug fixes
- tasks order
