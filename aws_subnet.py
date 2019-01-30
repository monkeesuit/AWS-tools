#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, SUBNET
from aws_info import vpc_info

def subnets(environment,table_flag=False):
 
  field_names = ['Environment','ID','Name','VPC(ID/Name)','Zone','CIDR']
  subnet_json = query('describe-subnets',environment)
  subnet_data = jmespath.search(SUBNET, subnet_json)
  vpc2name = vpc_info(environment)
  
  csv_data = [
    [environment,
     subnet['id'],
     subnet['tag'],
     '{vpc_id}/{name}'.format(
       vpc_id = subnet['vpcId'],
       name = vpc2name.get(subnet['vpcId'],'-')
     ),
     subnet['zone'],
     subnet['cidr']
    ]
    for subnet in subnet_data
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

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  subnets(ENVIRONMENT,table_flag=True)

 
