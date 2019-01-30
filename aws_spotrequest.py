#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, SPOTREQUEST


def spot_requests(environment,table_flag=False):
 
  field_names = ['Environment','ID','Instance ID','Launched Zone','Image ID','Key Name','Instance Type','Type','Create Time','Spot Price','Status Code']
  spot_request_json = query('describe-spot-instance-requests',environment)
  spot_request_data = jmespath.search(SPOTREQUEST, spot_request_json)
  
  csv_data = [
    [environment,
     spot_request['id'],
     spot_request['instId'],
     spot_request['launchedZone'],
     spot_request['imgId'],
     spot_request['keyName'],
     spot_request['instType'],
     spot_request['type'],
     spot_request['createTime'],
     spot_request['spotPrice'],
     spot_request['statusCode'],
    ]
    for spot_request in spot_request_data
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
  spot_requests(ENVIRONMENT,table_flag=True)

 
