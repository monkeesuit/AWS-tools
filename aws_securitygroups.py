#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, SECURITYGROUP
from aws_ip import define_ip_addresses, name_ips
from aws_info import security_group_info


def lookup_tags(environment,permission,ip_dict,security_group_dict):

  tagged = []
  untagged = []

  for ip_entry in permission['ip']:

    if ip_entry['tag'] != None:

      tagged.append('{tag:20} ==> {address:20}'.format(
        tag = ip_entry['tag'],
        address = ip_entry['address']
       ))

    elif ip_dict.get(ip_entry['address']) != None:

      tagged.append('{tag:20} ==> {address:20}'.format(
        tag = ip_dict.get(ip_entry['address']),
        address = ip_entry['address']
       ))

    else:

      untagged.append(ip_entry['address'])

  for security_group_entry in permission['sg']:

    tagged.append('{name:20} ==> {security_group_id:20}'.format(
      name = security_group_dict.get(security_group_entry)['name'],
      security_group_id = security_group_entry
    ))

  return sorted(tagged),sorted(untagged)


def format_port_protocol(permission):

  if permission['portStart'] == permission['portEnd']:

    formatted = ['{}/{}'.format(
      permission['portStart'],
      permission['protocol']
    )]

  else:

    formatted = ['{}/{}/{}'.format(
      permission['portStart'],
      permission['portEnd'],
      permission['protocol']
     )]

  return formatted


def format_permission_rule(environment,permission,ip_dict,security_group_dict):

  port_protocol = format_port_protocol(permission)
  tagged, untagged = lookup_tags(environment,permission,ip_dict,security_group_dict)

  num_tagged = len(tagged)
  num_untagged = len(untagged)
  if num_tagged >= num_untagged:

      port_protocol += ([''] * (num_tagged))
      tagged += ['']
      untagged += ([''] * (num_tagged - num_untagged + 1))

  else:

      port_protocol += ([''] * (num_untagged))
      tagged += ([''] * (num_untagged - num_tagged + 1))
      untagged += ['']

  return port_protocol, tagged, untagged


def security_groups(environment,table_flag=False):
 
  field_names = ['Environment','Name']
  security_group_json = query('describe-security-groups',environment)
  security_group_data = jmespath.search(SECURITYGROUP, security_group_json)
  
  ip_csv = [
      [environment,
       security_group['name'],
       security_group['id'],
       security_group['name'],
       security_group_rule['portStart'],
       security_group_rule['portEnd'],
       security_group_rule['protocol'],
       security_group_rule_ip['address'],
       security_group_rule_ip['tag'],
      ]
      for security_group in security_group_data
      for security_group_rule in security_group['ingressPermission']
      for security_group_rule_ip in security_group_rule['ip']
      ]
  sg_csv = [
      [environment,
       security_group['name'],
       security_group['id'],
       security_group_rule['portStart'],
       security_group_rule['portEnd'],
       security_group_rule['protocol'],
       security_group_rule_sg,
      ]
      for security_group in security_group_data
      for security_group_rule in security_group['ingressPermission']
      for security_group_rule_sg in security_group_rule['sg']
      if len(security_group_rule['sg']) > 0
      ]
  csv_data = ip_csv + sg_csv

  if table_flag==False:

    csv_writer = csv.writer(sys.stdout)
    csv_data.insert(0,field_names)
    for line in csv_data:
      csv_writer.writerow(line)

  else:

    ip_dict = name_ips(define_ip_addresses(environment))
    security_group_dict = security_group_info(environment)
    table_data = []
    for security_group in security_group_data:
      port_protocol_entry = []
      tagged_entry = []
      untagged_entry = []
      for security_group_permission in security_group['ingressPermission']:
  
        port_protocol_rule, tagged_members, untagged_members = format_permission_rule(environment,security_group_permission,ip_dict,security_group_dict)
  
        port_protocol_entry.append('\n'.join(port_protocol_rule))
        tagged_entry.append('\n'.join(tagged_members))
        untagged_entry.append('\n'.join(untagged_members))
  
      port_protocol_string = '\n'.join(port_protocol_entry)
      tagged_string = '\n'.join(tagged_entry)
      untagged_string = '\n'.join(untagged_entry)
  
      table_data.append([
        environment,
        security_group['name'],
        security_group['id'],
        port_protocol_string,
        tagged_string,
        untagged_string
      ])
  
    table_data=sorted(table_data, key=lambda table_entry:table_entry[1])
    table_data.insert(0,['Environment','Name','ID','Ports','Tagged Members','Untagged Members'])
    table = SingleTable(table_data)
    table.inner_row_border = True
    print table.table


###############################################################################

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  security_groups(ENVIRONMENT)

 
