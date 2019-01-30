#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, RESERVEDINSTANCE


def reserved_instances(environment,table_flag=False):
 
  field_names = ['Environment','ID','Offer Type','Zone','Charge Amount','Charge Frequency','Start','End','Instance Type','Instance Count']
  reserved_instance_json = query('describe-reserved-instances',environment)
  reserved_instance_data = jmespath.search(RESERVEDINSTANCE, reserved_instance_json)
  
  csv_data = [
    [environment,
     reserved_instance['id'],
     reserved_instance['offerType'],
     reserved_instance['zone'],
     reserved_instance_charge['amount'],
     reserved_instance_charge['freq'],
     reserved_instance['start'],
     reserved_instance['end'],
     reserved_instance['instType'],
     reserved_instance['instCount'],
     reserved_instance['fixedPrice'],
     reserved_instance['state'],
    ]
    for reserved_instance in reserved_instance_data
    for reserved_instance_charge in reserved_instance['charge']
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
  reserved_instances(ENVIRONMENT,table_flag=True)

 
