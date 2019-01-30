#!/usr/bin/env python

import jmespath
import argparse
import csv
import sys
from terminaltables import SingleTable
from aws_queries import query, VOLUME
from aws_info import instance_info

def collect(environment,data):

  final_data = []
  hosts = list(set([
    line[1]
    for line in data
  ]))
  for host in hosts:
    devices = []
    sizes = []
    names = []
    ids = []
    types = []
    iops = []
    encrypted = []
    delete = []
    for line in data:
      if host==line[1]:
        devices.append(str(line[2]))
        sizes.append(str(line[3]))
        names.append(str(line[4]))
        ids.append(str(line[5]))
        types.append(str(line[6]))
        iops.append(str(line[7]))
        encrypted.append(str(line[8]))
        delete.append(str(line[9]))
    final_data.append([
      environment,
      host,
      '\n'.join(devices),
      '\n'.join(sizes),
      '\n'.join(names),
      '\n'.join(ids),
      '\n'.join(types),
      '\n'.join(iops),
      '\n'.join(encrypted),
      '\n'.join(delete)
    ])

  return final_data

def volumes(environment,table_flag=False):
 
  field_names = ['Environment','Instance(ID/Name)','Device','Size','Name','Id','Type','IOPS','Encrypted','Delete on Termination']
  volume_json = query('describe-volumes',environment)
  volume_data = jmespath.search(VOLUME, volume_json)
  instance2name = instance_info(environment)

  csv_data = [
    [environment,
     '{id}/{name}'.format(id = volume['instId'], name = instance2name.get(volume['instId'], '-')),
     volume['device'],
     '{} {}'.format(volume['size'], 'GB'),
     volume['tag'],
     volume['id'],
     volume['type'],
     volume['iops'],
     'Encrypted' if volume['encrypted']=='True' else 'Not Encrypted',
     'Delete' if volume['delete']=='True' else 'Don\'t Delete'
    ]
    for volume in volume_data
  ]
  csv_data=sorted(csv_data, key=lambda x: (x[1].split('/')[1],x[2]))

  if table_flag==False:
    csv_data.insert(0,field_names)
    csv_writer = csv.writer(sys.stdout)
    for line in csv_data:
      csv_writer.writerow(line)
  else:
    # Group volumes by instance (i.e. one entry per instance with all info in single entry)
    table_data=collect(environment,csv_data)
    table_data=sorted(table_data, key=lambda x: x[1].split('/')[1])
    table = SingleTable(table_data)
    table.inner_row_border = True
    print table.table

###############################################################################

if __name__=="__main__":

  parser = argparse.ArgumentParser()
  parser.add_argument('environment',nargs=1)
  args = parser.parse_args()

  ENVIRONMENT=args.environment[0]
  volumes(ENVIRONMENT,table_flag=True)

 
