#!/usr/bin/env python

from subprocess import Popen, PIPE
import getpass
import json

USER=getpass.getuser()

def query(ec2_action,environment):

  ec2_query = 'aws ec2 {action} --profile {user}{env}'
  command = ec2_query.format(
    action=ec2_action,
    user=USER,
    env=environment,
    extra=''
  )
  #print command
  subshell = Popen(
    command.split(),
    stdout=PIPE,
    stderr=PIPE
  )
  out, err = subshell.communicate()
  json_data = json.loads(out)


  return json_data

SECURITYGROUP = (
"SecurityGroups[].{"
  + "id: GroupId,"
  + "name: GroupName,"
  + "ingressPermission: IpPermissions[].{"
    + "portStart: FromPort,"
    + "portEnd: ToPort,"
    + "protocol: IpProtocol,"
    + "sg: UserIdGroupPairs[].GroupId,"
    + "ip: IpRanges[].{"
      + "address: CidrIp,"
      + "tag: Description"
    + "}"
  + "},"
  + "egressPermission: IpPermissionsEgress[].{"
    + "portStart: FromPort,"
    + "portEnd: ToPort,"
    + "protocol: IpProtocol,"
    + "sg: UserIdGroupPairs[].GroupId,"
    + "ip: IpRanges[].{"
      + "address: CidrIp,"
      + "tag: Description"
    + "}"
  + "}"
+ "}"
)

INSTANCE = (
"Reservations[].{"
  + "tag: Instances[].Tags[?Key==`Name`].Value | [0] | [0],"
  + "id: Instances[].InstanceId | [0],"
  + "type: Instances[].InstanceType | [0],"
  + "launchTime: Instances[].LaunchTime | [0],"
  + "resId: ReservationId,"
  + "virtType: Instances[].VirtualizationType | [0],"
  + "state: Instances[].State.Name | [0],"
  + "ip: Instances[].{"
    + "pub: PublicIpAddress,"
    + "prv: PrivateIpAddress"
  + "} | [0],"
  + "imageId: Instances[].ImageId | [0],"
  + "key: Instances[].KeyName | [0],"
  + "subnetId: Instances[].SubnetId | [0],"
  + "zone: Instances[].Placement.AvailabilityZone | [0],"
  + "cycle: Instances[].InstanceLifecycle | [0],"
  + "sg: Instances[].SecurityGroups[].{"
    + "name: GroupName,"
    + "id: GroupId"
  + "}"
+ "}"
)

AVAILABILITYZONE = (
"AvailabilityZones[]."
  + "{name: ZoneName}"
)

IMAGE = (
"Images[].{"
  + "id: ImageId,"
  + "name: Name,"
  + "virtType: VirtualizationType,"
  + "rootType: RootDeviceType,"
  + "ownerId: OwnerId,"
  + "createDate: CreationDate"
+ "}"
)

KEYPAIR = (
"KeyPairs[].{name: KeyName}"
)

NETWORKACL = (
"NetworkAcls[].{"
  + "tag: Tags[?Key==`Name`].Value | [0]"
  + "id: NetworkAclId,"
  + "vpcId: VpcId,"
  + "entries: Entries[].{"
    + "ruleNum: RuleNumber,"
    + "protocol: Protocol,"
    + "portRange: PortRange[].{"
      + "start: To,"
      + "end: From"
    + "},"
    + "action: RuleAction,"
    + "cidr: CidrBlock"
  + "}"
+ "}"
)

RESERVEDINSTANCE = (
"ReservedInstances[].{"
  + "id: ReservedInstancesId,"
  + "offerType: OfferingType,"
  + "zone: AvailabilityZone,"
  + "charge: RecurringCharges[].{"
    + "amount: Amount,"
    + "freq: Frequency"
  + "},"
  + "start: Start,"
  + "end: End,"
  + "instType: InstanceType,"
  + "instCount: InstanceCount,"
  + "fixedPrice: FixedPrice,"
  + "state: State"
"}"
)

SPOTREQUEST = (
"SpotInstanceRequests[].{"
  + "id: SpotInstanceRequestId,"
  + "instId: InstanceId,"
  + "launchedZone: LaunchedAvailabilityZone,"
  + "imgId: LaunchSpecification.ImageId,"
  + "keyName: LaunchSpecification.KeyName,"
  + "instType: LaunchSpecification.InstanceType,"
  + "type: Type,"
  + "createTime: CreateTime,"
  + "spotPrice: SpotPrice,"
  + "statusCode: Status.Code"
+ "}"
)

SUBNET = (
"Subnets[].{"
  + "id: SubnetId,"
  + "tag: Tags[?Key==`Name`].Value | [0],"
  + "vpcId: VpcId,"
  + "cidr: CidrBlock,"
  + "zone: AvailabilityZone"
+ "}"
)

VOLUME = (
"Volumes[].{"
  + "id: VolumeId,"
  + "tag: Tags[?Key==`Name`].Value | [0],"
  + "type: VolumeType,"
  + "instId: Attachments[].InstanceId | [0],"
  + "device: Attachments[].Device | [0],"
  + "size: Size,"
  + "iops: Iops,"
  + "encrypted: Encrypted,"
  + "delete: Attachments[].DeleteOnTermination | [0]"
+ "}"
)
