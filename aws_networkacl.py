#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, NETWORKACL
from aws_info import vpc_info

def network_acls(environment,table_flag=False):
 
  field_names = ['Environment','ID','Name','VPC(ID/Name)','Rule Number','Port Range','Protocol','Action','CIDR']
  network_acl_json = query('describe-network-acls',environment)
  network_acl_data = jmespath.search(NETWORKACL, network_acl_json)
  vpc2name = vpc_info(environment)
  
  csv_data = [
    [environment,
     network_acl['id'],
     network_acl['tag'],
     '{vpc_id}/{name}'.format(
       vpc_id = network_acl['vpcId'],
       name = vpc2name.get(network_acl['vpcId'],'-')
     ),
     network_acl_entry['ruleNum'],
     network_acl_entry['portRange'],
     network_acl_entry['protocol'],
     network_acl_entry['action'],
     network_acl_entry['cidr']
    ]
    for network_acl in network_acl_data
    for network_acl_entry in network_acl['entries']
  ]
  csv_data.insert(0,field_names)

  if table_flag==False:
    csv_writer = csv.writer(sys.stdout)
    for line in csv_data:
      csv_writer.writerow(line)
  else:
    table = SingleTable(csv_data)
    table.inner_row_border = True
    print table.table

###############################################################################
## http://www.iana.org/assignments/protocol-numbers/protocol-numbers.xhtml - protocol integer definitions

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  network_acls(ENVIRONMENT,table_flag=True)

 
