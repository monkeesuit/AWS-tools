#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from collections import namedtuple
from terminaltables import SingleTable
from aws_queries import query, INSTANCE
from aws_info import security_group_info
from aws_ip import define_ip_addresses, name_ips

sys


def format_port(port):

  if port[0]==port[1]:
    port_string = '{}/{}'.format(str(port[0]),str(port[2]))
  else:
    port_string = '{}/{}/{}'.format(str(port[0]),str(port[1]),str(port[2]))

  return port_string


def ips_granted_access_over_port(port,attached_security_groups,ip_dict,security_group_dict,long_flag):

  port_members = []
  for security_group in attached_security_groups:

    try:
      ip_addresses = security_group_dict[security_group['id']]['members'][port]
    except KeyError:
      continue

    if long_flag==True:
      port_members += [
        '{name:20} {address:20} {sg_id:20} {sg_name:20}'.format(
          name=ip_dict.get(ip_address,'None'),
          address=ip_address,
          sg_id=security_group['id'],
          sg_name=security_group_dict[security_group['id']]['name']
        )
        for ip_address in ip_addresses
        if '{:20} {:20} {:20} {:20}'.format(
          ip_address,
          ip_dict.get(ip_address,'None'),
          security_group['id'],
          security_group_dict[security_group['id']]['name']
        ) not in port_members
      ]
    else:
      port_members += [
        '{name:20}'.format(
          name=ip_dict.get(ip_address,'None'),
          address=ip_address,
          sg_id=security_group['id'],
          sg_name=security_group_dict[security_group['id']]['name']
        )
        for ip_address in ip_addresses
        if '{:20}'.format(
          ip_address,
          ip_dict.get(ip_address,'None'),
          security_group['id'],
          security_group_dict[security_group['id']]['name']
        ) not in port_members
      ]

  return sorted(port_members)


def make_host_entry(host,ip_dict,security_group_dict,long_flag):

  open_ports = list(set([
    port
    for security_group in host['sg']
    for port in security_group_dict[security_group['id']]['members'].keys()
  ]))

  ports_entry = []
  members_entry = []
  for port in open_ports:

    port_members = ips_granted_access_over_port(port,host['sg'],ip_dict,security_group_dict,long_flag)
    port_string = format_port(port)

    ports_entry += ([port_string] + (['']*len(port_members)))
    members_entry += (port_members + [''])

  return ports_entry, members_entry


def access(environment,host_query='all',table_flag=False,long_flag=False):
 
  if table_flag==False:

    sys.stderr.write('This report does not generate csv output...')
    sys.stderr.write('Please use the table flag (--table)!')
    sys.exit(1)

  if long_flag==True:
    field_names = []
  else:
    field_names = []

  instance_json = query('describe-instances',environment)
  instance_data = jmespath.search(INSTANCE, instance_json)
  ip_dict = name_ips(define_ip_addresses(environment))
  security_group_dict = security_group_info(environment)

  table_data = []
  if host_query=='all':
    for host in instance_data:
      ports_entry, members_entry = make_host_entry(host,ip_dict,security_group_dict,long_flag)
      ports_string = '\n'.join(ports_entry)
      members_string = '\n'.join(members_entry)

      if long_flag==True:
        table_data.append([
          environment,
          host['tag'],
          host['id'],
          ports_string,
          members_string
        ])
      else:
        table_data.append([
          environment,
          host['tag'],
          ports_string,
          members_string
        ])
  else:
    for host in instance_data:
      if host['tag']==host_query:
        break
    ports_entry, members_entry = make_host_entry(host,ip_dict,security_group_dict,long_flag)
    ports_string = '\n'.join(ports_entry)
    members_string = '\n'.join(members_entry)

    if long_flag==True:
      table_data.append([
        environment,
        host['tag'],
        host['id'],
        ports_string,
        members_string
      ])
    else:
      table_data.append([
        environment,
        host['tag'],
        ports_string,
        members_string
      ])

  table_data=sorted(table_data, key = lambda entry:entry[1])
  table = SingleTable(table_data)
  table.inner_row_border = True
  print table.table

###############################################################################

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  access(ENVIRONMENT,'all',table_flag=True,long_flag=True)

 
