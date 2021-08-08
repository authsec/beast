#!/usr/local/bin/python3

import sys, argparse
import os
import csv
import time

DEFAULT_SYNC_FORMAT_STRING="imapsync --nosyncacls --subscribe --syncinternaldates --fast --host1 \'{from_host}\' --port1 {from_host_port} --user1 \'{account.host1_username}\' --password1 \'{account.host1_password}\' --ssl1 --host2 \'{to_host}\' --port2 {to_host_port} --user2 \'{account.host2_username}\' --password2 \'{account.host2_password}\' --ssl2 --delete2"

class SmartFormatter(argparse.HelpFormatter):
    def _split_lines(self, text, width):
        if text.startswith('R|'):
            return text[2:].splitlines()  
        # this is the RawTextHelpFormatter._split_lines
        return argparse.HelpFormatter._split_lines(self, text, width)

class StatsEntry:
    def __init__(self, host1, host2, host1_username, host2_username, start_time, end_time):
        self.host1 = host1
        self.host2 = host2
        self.host1_username = host1_username
        self.host2_username = host2_username
        self.start_time = start_time
        self.end_time = end_time

class Stats:
    @staticmethod
    def print_summary(stats_entries):
        print("Migrated Account")
        for stats_entry in stats_entries:
            print(f"\t{stats_entry.host1}::{stats_entry.host1_username} to {stats_entry.host2}::{stats_entry.host2_username} in {stats_entry.end_time - stats_entry.start_time} seconds")


class ExampleFileAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        accounts_file_example='''
# Comments are allowed if you want to link to some server settings
"from_host_username","from_host_password","to_host_username","to_host_password"
"j@example.org","example_passwd"
"g@example.org","example_from_passwd","g_new@example.net","example_to_passwd"
"superdud@example.com","example_from_passwd","superdude@example.net","example_to_dude_passwd"
"megaman@example.net","example_from_passwd","mega@example.com"
"louis.megaman@example.net","example_from_passwd","mega@example.com"
"Pippi.Langstrumpf@example.net","example_from_passwd","","new_to_passwd"

    '''
        print(accounts_file_example)
        parser.exit()

class PrintParsedAccountsAction(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        accounts = Account.read_accounts(namespace.accounts_csv_file_name)
        for account in accounts:
            print(f"From Host: ['{account.host1_username:>32}', '{account.host1_password:>32}'], To Host: ['{account.host2_username:>32}', '{account.host2_password:>32}']")
        parser.exit()

class BEASTParser(argparse.ArgumentParser):
    def error(self, message):
        sys.stderr.write(f"My bad, couldn't handle {message}\nPlease try the following:\n\n")
        self.print_help()
        sys.exit(2)

class Account:
    def __init__(self, host1_username, host1_password, host2_username,
                 host2_password):
        self.host1_username = host1_username
        self.host1_password = host1_password
        self.host2_username = host2_username
        self.host2_password = host2_password

    @staticmethod
    def read_accounts(accounts_csv_file):
        accounts = []
        with open(accounts_csv_file) as accounts_file:
            accounts_reader = csv.DictReader(filter(lambda row: row[0]!='#', accounts_file))
            for account in accounts_reader:
                to_host_username = account['to_host_username']
                to_host_password = account['to_host_password']
    
                if not to_host_username or to_host_username == "":
                    #print(f"Empty to_host_username, assuming same as from_host_username")
                    to_host_username = account['from_host_username']
    
                if not to_host_password or to_host_password == "":
                    #print(f"Empty to_host_password, assuming same as from_host_password")
                    to_host_password = account['from_host_password']
    
                accounts.append(
                    Account(account['from_host_username'],
                            account['from_host_password'], to_host_username,
                            to_host_password))
    
        return accounts

def assemble_sync_command(sync_format_string, account, from_host, from_host_port, to_host, to_host_port, dry_run):
    # This trick lets you define a different execution command string on the command line if you need one, while still being able to use the account class variables and contents.
    command = eval(f'f"""{sync_format_string}"""')
    
    if dry_run:
        command += " --dry"

    return command

stats_entries = []
def sync_account(sync_format_string, account, from_host, from_host_port, to_host, to_host_port,
                 dry_run):
    sync_command = assemble_sync_command(sync_format_string, account, from_host, from_host_port, to_host, to_host_port, dry_run)

    start_time = time.perf_counter()
    print(f"[{time.asctime()}] Synchronizing Account {account.host1_username}")
    os.system(sync_command)
    stats_entries.append(StatsEntry(from_host, to_host, account.host1_username, account.host2_username, start_time, time.perf_counter()))

def main(args):
    from_host = args.from_host
    from_host_port = args.from_host_port
    to_host = args.to_host
    to_host_port = args.to_host_port
    dry_run = args.dry_run
    accounts_csv_file_name = args.accounts_csv_file_name
    sync_format_string = args.sync_format_string

    accounts = Account.read_accounts(accounts_csv_file_name)

    if  args.only_assemble_sync_command:
        for account in accounts:
            print(assemble_sync_command(sync_format_string, account, from_host, from_host_port, to_host, to_host_port, dry_run))
    else:
        for account in accounts:
            sync_account(sync_format_string, account, from_host, from_host_port, to_host, to_host_port,dry_run)
        
        Stats.print_summary(stats_entries)
    
if __name__ == '__main__':
    parser = BEASTParser(description="Bulk Email Account Synchronization Tool (BEAST)", formatter_class=SmartFormatter)
    parser.add_argument("--from-host",metavar='SRC_HOST',required=True,help="The fully qualified (source) hostname from which you want to sync")
    parser.add_argument("--to-host",metavar='DST_HOST',required=True,help="The fully qualified (destination) hostname where you want to sync to")
    parser.add_argument("--dry-run",action="store_true",help="Whether or not you want to execute a real run")
    parser.add_argument("--accounts-csv-file-name",default="accounts.csv",help="The name of the accounts CSV file that beast should use. Run --print-accounts-csv-file-example to get an example file.")
    parser.add_argument("-e","--print-accounts-csv-file-example",nargs=0,action=ExampleFileAction,help="Display an example file for bulk synchronization.")
    parser.add_argument("-p","--print-accounts",nargs=0,action=PrintParsedAccountsAction,help="Display a list of effectively used accounts and passwords. Note: If you use an alternative file name you need to specify --accounts-csv-file-name BEFORE -p")
    parser.add_argument("-o","--only-assemble-sync-command",action="store_true",help="Display a list of effectively used accounts and passwords. Note: If you use an alternative file name you need to specify --accounts-csv-file-name BEFORE -p")
    parser.add_argument("--from-host-port",metavar='SRC_PORT',type=int,default=993,help="The port of the source host where the IMAP service is running")
    parser.add_argument("--to-host-port",metavar='SRC_PORT',type=int,default=993,help="The port of the destination host to where you want to sync to")
    parser.add_argument("--sync-format-string",default=DEFAULT_SYNC_FORMAT_STRING, help="This flag lets you specify a custom imapsync format string, while still being able to use the bulk sync mechanism.")

    args = parser.parse_args()

    if len(sys.argv) == 0:
        parser.print_help(sys.stderr)
        sys.exit(1)

    main(args)


