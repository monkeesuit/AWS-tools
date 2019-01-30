#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, INSTANCE
from aws_info import subnet_info


def instances(environment,long_flag=False,table_flag=False):
 
  instance_json = query('describe-instances',environment)
  instance_data = jmespath.search(INSTANCE, instance_json)
  
  if long_flag==False:
    field_names = ['Name','ID','Type','State','Private IP','Public IP','Environment']
    csv_data = [
      [instance['tag'],
       instance['id'],
       instance['type'],
       instance['state'],
       instance['ip']['prv'],
       instance['ip']['pub'],
       environment
      ]
      for instance in instance_data
    ]
  else:
    subnet2name = subnet_info(environment)
    field_names = ['Name','ID','Type','State','Private IP','Public IP','Launch Time','Image ID','Reservation ID','Virtualization Type','Key','Subnet(ID/Name)','Environment']
    csv_data = [
      [instance['tag'],
       instance['id'],
       instance['type'],
       instance['state'],
       instance['ip']['prv'],
       instance['ip']['pub'],
       instance['launchTime'],
       instance['imageId'],
       instance['resId'],
       instance['virtType'],
       instance['key'],
       '{sub_id}/{name}'.format(
          sub_id=instance['subnetId'],
          name=subnet2name.get(instance['subnetId'],'-')
       ),
       environment
      ]
      for instance in instance_data
    ]

  csv_data.sort()
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
  parser.add_argument('--long',action='store_true')
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  LONG=args.long
  instances(ENVIRONMENT,LONG,table_flag=True)

 
