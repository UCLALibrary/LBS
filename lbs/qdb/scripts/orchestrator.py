#!/usr/bin/env python3

import argparse
import arrow
import os
import psycopg2
from sys import exit

from qdb.scripts.settings import REPORTS_DIR, DEFAULT_RECIPIENTS, UL_NAME
from qdb.scripts import fetcher, formatter, sender
from qdb.scripts.parser import Parser


class Orchestrator():

    def __init__(self, reports_dir, recipients):
        self.reports_dir = reports_dir
        self.recipients = recipients
        self.conn = self.get_conn()
        self.cursor = self.conn.cursor()
        self.cursor.execute(
            'SELECT * FROM qdb_unit ORDER BY name')
        fetch_results = self.cursor.fetchall()

    def get_conn(self):
        conn = psycopg2.connect(
            "host=db dbname=qdb user=qdb_user password=dev_qdb_pass")
        return conn

    def validate_date(self, year=None, month=None, yyyymm=False):
        today = arrow.now()
        if year is None and month is None:
            report_date = today.shift(months=-1)
            month = report_date.month
            year = report_date.year
        elif not (year and month):
            raise ValueError(
                "ERROR: You must supply both year and month or neither")
        elif month < 1 or month > 12:
            raise ValueError("ERROR: month must be a number from 1 to 12")
        elif arrow.get(year=year, month=month, day=1) > today:
            raise ValueError("ERROR: cannot request a future report")
        if yyyymm is True:
            return f'{year}{month:02}'
        return year, month

    def get_all_units(self):
        self.cursor.execute('SELECT * FROM qdb_unit ORDER BY name')
        results = self.cursor.fetchall()
        return results

    def list_units(self):
        units = self.get_all_units()
        name_length = max([len(u[1]) for u in units])
        header = 'ID | Name'
        bar = '---|' + '-' * name_length
        msg = [header, bar]
        for row in units:
            msg.append(f'{row[0]:>2} | {row[1]}')
        return '\n'.join(msg)

    def validate_units(self, unit_ids=None):
        # similar: match multiple rows in MYSQL with info from python list
        if unit_ids is None or 28 in unit_ids:
            return self.get_all_units()
        qms = ','.join(['%s']*len(unit_ids))
        cmd = f'SELECT * FROM qdb_unit WHERE id IN ({qms})'
        self.cursor.execute(cmd, unit_ids)
        rows = self.cursor.fetchall()
        if len(rows) < len(unit_ids):
            bad_ids = set(unit_ids) - set([r['id'] for r in rows])
            raise ValueError(f"ERROR: Unit ID does not exist {bad_ids}")
        return rows

    def get_accounts_for_unit(self, unit_id):
        # separate Library Materials (LM) from other cost centers, as requested
        cmd = '''
            SELECT qdb_account.account, string_agg(qdb_account.cost_center, ',') AS cc_list
            FROM qdb_account, qdb_unit
            WHERE qdb_account.cost_center != 'LM'
            AND qdb_account.cost_center != ''
            AND qdb_account.unit_id = qdb_unit.id
            AND qdb_unit.id = %s
            GROUP BY qdb_account.account
            UNION
            SELECT qdb_account.account, qdb_account.cost_center AS cc_list
            FROM qdb_account, qdb_unit
            WHERE qdb_account.cost_center = 'LM'
            AND qdb_account.unit_id = qdb_unit.id
            AND qdb_unit.id = %s'''
        self.cursor.execute(cmd, [unit_id, unit_id])
        results = self.cursor.fetchall()
        return [(row[0], row[1].split(',')) for row in sorted(results)]

    def cleanup_reports_dir(self):
        for f in os.listdir(self.reports_dir):
            if f == '.gitignore':
                continue
            try:
                os.remove(os.path.join(self.reports_dir, f))
            except:  # pragma: no cover
                print(f'Could not delete from reports directory: {f}')

    def get_recipients(self, unit_id, unit_name):
        recipients = set(self.recipients)
        cmd = '''
            SELECT email
            FROM qdb_staff, qdb_unit, qdb_recipient
            WHERE qdb_recipient.unit_id = %s
            AND qdb_staff.name != %s'''
        if unit_name == 'LBS':
            cmd += " AND (qdb_staff.id = qdb_recipient.recipient_id AND qdb_recipient.role = 'head')"
        else:
            cmd += " AND ((qdb_staff.id = qdb_recipient.recipient_id AND qdb_recipient.role = 'head') OR (qdb_staff.id = qdb_recipient.recipient_id AND qdb_recipient.role = 'aul') OR (qdb_staff.id = qdb_recipient.recipient_id AND qdb_recipient.role = 'assoc'))"
        self.cursor.execute(cmd, [unit_id, UL_NAME])
        recipients.update([r[0] for r in self.cursor.fetchall()])
        return recipients

    def generate_filename(self, unit_name, yyyymm):
        name = f"{unit_name.replace(' ','_')}_{yyyymm[:4]}_{yyyymm[4:]}.xlsx"
        return os.path.join(self.reports_dir, name)

    def run(self, yyyymm, units, send_email=False, override_recipients=None, list_recipients=False):
        for unit in units:
            unit_id = unit[0]
            unit_name = unit[1]
            if override_recipients is not None:
                recipients = override_recipients
            else:
                recipients = self.get_recipients(unit_id, unit_name)
            if list_recipients is True:
                print(f"{unit_name} recipients:")
                for r in sorted(recipients):
                    print(f'-- {r}')
                continue
            parser = Parser(yyyymm, unit_name)
            for account, cc_list in self.get_accounts_for_unit(unit_id):
                print(
                    f'running {yyyymm} report of {account}{cc_list} for unit {unit_name}')
                rows = fetcher.get_qdb_data(yyyymm, account, cc_list)
                if len(rows) == 0:  # pragma: no cover
                    print(f'No data from QDB for {account}{cc_list}')
                    continue
                result = parser.add_account(account, cc_list, rows)
                if result is False:  # pragma: no cover
                    print(f'Account {account} is empty. Exclude from report')
            if len(parser.data['accounts']) == 0:  # pragma: no cover
                print(f'All accounts empty. No report generated for {unit}')
                continue
            filename = self.generate_filename(unit_name, yyyymm)
            formatter.generate_report(parser.data, filename)
            if send_email is True:
                sender.send_report(parser.data, filename, recipients)
                os.remove(filename)
                print(f'sent report {filename} to {recipients}')
            else:
                print(f'generated report at {filename}')


if __name__ == "__main__":  # pragma: no cover
    ap = argparse.ArgumentParser()
    ap.add_argument("-l", "--list_units", action="store_true",
                    help="List all the units")
    ap.add_argument("-y", "--year", type=int,
                    help="Year of the report")
    ap.add_argument("-m", "--month", type=int,
                    help="Month number of the report")
    ap.add_argument("-u", "--units", nargs='+',
                    help="Unit ID number; if omitted all units will receive reports")
    ap.add_argument("-e", "--email", action="store_true",
                    help="Email the report to the recipients")
    ap.add_argument("-r", "--list_recipients", action="store_true",
                    help="Display the list of people to email for each report")
    args = ap.parse_args()
    try:
        orchestrator = Orchestrator(REPORTS_DIR, DEFAULT_RECIPIENTS)
        if args.list_units is True:
            print(orchestrator.list_units())
            exit(0)
        yyyymm = orchestrator.validate_date(args.year, args.month, yyyymm=True)
        units = orchestrator.validate_units(args.units)
        orchestrator.run(yyyymm, units, send_email=args.email,
                         list_recipients=args.list_recipients)
    except ValueError as e:
        exit(e)
