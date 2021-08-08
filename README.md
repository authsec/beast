# Bulk Email Account Synchronization Tool (BEAST)

The idea of BEAST is to provide a simple way of (IMAP) synchronizing mail servers with each other. 

This is typically useful if you are required to migrate a lot of mailboxes at a time from one IMAP server to another.

In order to migrate your accounts simply create an `accounts.csv` file with the following content:

```
"from_host_username","from_host_password","to_host_username","to_host_password"
"j@example.org","example_passwd"
"g@example.org","example_from_passwd","g_new@example.net","example_to_passwd"
"superdud@example.com","example_from_passwd","superdude@example.net","example_to_dude_passwd"
"megaman@example.net","example_from_passwd","mega@example.com"
"louis.megaman@example.net","example_from_passwd","mega@example.com"
"Pippi.Langstrumpf@example.net","example_from_passwd","","new_to_passwd"
```

If you omit the `to_host_username` and/or the `to_host_password` column, BEAST will assume you are using the same credential set on the destination machine.

# Getting Help

BEAST is willing to help you if you ask nicely.

``` bash
#> docker run --rm --name beast -v $(pwd):/beast authsec/beast -h
usage: beast.py [-h] --from-host SRC_HOST --to-host DST_HOST [--dry-run]
                [--accounts-csv-file-name ACCOUNTS_CSV_FILE_NAME] [-e] [-p]
                [-o] [--from-host-port SRC_PORT] [--to-host-port SRC_PORT]
                [--sync-format-string SYNC_FORMAT_STRING] [-l]

Bulk Email Account Synchronization Tool (BEAST)

optional arguments:
  -h, --help            show this help message and exit
  --from-host SRC_HOST  The fully qualified (source) hostname from which you
                        want to sync
  --to-host DST_HOST    The fully qualified (destination) hostname where you
                        want to sync to
  --dry-run             Whether or not you want to execute a real run
  --accounts-csv-file-name ACCOUNTS_CSV_FILE_NAME
                        The name of the accounts CSV file that beast should
                        use. Run --print-accounts-csv-file-example to get an
                        example file.
  -e, --print-accounts-csv-file-example
                        Display an example file for bulk synchronization.
  -p, --print-accounts  Display a list of effectively used accounts and
                        passwords. Note: If you use an alternative file name
                        you need to specify --accounts-csv-file-name BEFORE -p
  -o, --only-assemble-sync-command
                        Display a list of effectively used accounts and
                        passwords. Note: If you use an alternative file name
                        you need to specify --accounts-csv-file-name BEFORE -p
  --from-host-port SRC_PORT
                        The port of the source host where the IMAP service is
                        running
  --to-host-port SRC_PORT
                        The port of the destination host to where you want to
                        sync to
  --sync-format-string SYNC_FORMAT_STRING
                        This flag lets you specify a custom imapsync format
                        string, while still being able to use the bulk sync
                        mechanism.
  -l, --create-imapsync-logs
                        Write the imapsync logs to file for later review
```

# Example Usage

NOTE: If you don't want the log messages to be visible on the screen but instead be written to a log file, use the `-l` switch.

The below command will e.g. use the `accounts_org1.csv` in your current directory to assemble the sync commands that will be executed. 

``` bash
#> docker run --rm --name beast -v $(pwd):/beast authsec/beast --from-host mail.example.net --to-host mail.example.org -o --accounts-csv-file-name accounts_org1.csv
```

The below command shows you how you can change the command string to adapt it to your special needs should you only want to generate the sync command with BEAST.

``` bash
#> docker run --rm --name beast -v $(pwd):/beast authsec/beast --from-host mail.example.net --to-host mail.example.org -o --sync-format-string "/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 \'{from_host}\' --port1 {from_host_port} --user1 \'{account.host1_username}\' --password1 \'{account.host1_password}\' --ssl1 --host2 \'{to_host}\' --port2 {to_host_port} --user2 \'{account.host2_username}\' --password2 \'{account.host2_password}\' --ssl2 --delete2"
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'j@example.org' --password1 'example_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'j@example.org' --password2 'example_passwd' --ssl2 --delete2
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'g@example.org' --password1 'example_from_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'g_new@example.net' --password2 'example_to_passwd' --ssl2 --delete2
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'superdud@example.com' --password1 'example_from_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'superdude@example.net' --password2 'example_to_dude_passwd' --ssl2 --delete2
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'megaman@example.net' --password1 'example_from_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'mega@example.com' --password2 'example_from_passwd' --ssl2 --delete2
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'louis.megaman@example.net' --password1 'example_from_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'mega@example.com' --password2 'example_from_passwd' --ssl2 --delete2
/bin/my/special/path/to/imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 'mail.example.net' --port1 993 --user1 'Pippi.Langstrumpf@example.net' --password1 'example_from_passwd' --ssl1 --host2 'mail.example.org' --port2 993 --user2 'Pippi.Langstrumpf@example.net' --password2 'new_to_passwd' --ssl2 --delete2
```