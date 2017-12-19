# -*- coding: utf-8 -*-
import os
import pytz, datetime


script_path = os.path.dirname(__file__)
xml_path_inb = os.path.join(script_path, 'xml' , 'in')
xml_done_path_inb = os.path.join(script_path, 'xml' , 'in', 'done')
xml_path_outb = os.path.join(script_path, 'xml' , 'out')
xml_done_path_outb = os.path.join(script_path, 'xml' , 'out', 'done')

#time
local = pytz.timezone ("Europe/Moscow")

id_prefix = 'sp_'

# mysql portal
mysql_ip = '127.0.0.1'
# prom:
mysql_port = 3306
#local:
# mysql_port = 8889
mysql_user = ''
mysql_password = ''
mysql_dbname = ''

#mail
mail_subject = 'Sber-Oktava'
mail_sber_email = ''
mailuser_cfg = 'integration.oktava'
mailsender_cfg = ''
mailpass_cfg = ''
remove_email_cfg = 1
move_processed_xmls_cfg = 1

xml_out_name_cfg = 'from_oktava.xml'
outbound_xml_cfg = os.path.join(xml_path_outb,xml_out_name_cfg)

### STATUS - CLASSNAME DICT
#IN_PROGRESS
classname_status_dict = {'1': 'IN_PROGRESS', '2': 'IN_PROGRESS', '3': 'IN_PROGRESS', '7': 'DONE', '9': 'DONE'}

xml_start_cfg = '''<?xml version="1.0" encoding="utf-8"?>
<!DOCTYPE CIM PUBLIC "SYSTEM" "CIM_DTD_V20.dtd"[
<!ENTITY lt      "&#38;#60;">
<!ENTITY gt      "&#62;">
<!ENTITY amp     "&#38;#38;">
<!ENTITY apos    "&#39;">
<!ENTITY quot    "&#34;">]>
<CIM CIMVERSION="2.0" DTDVERSION="2.2">
<DECLARATION>
<DECLGROUP>
<VALUE.OBJECT>
<INSTANCE CLASSNAME="Header">
<PROPERTY NAME="Date" TYPE="string">
	<VALUE>'''+str(datetime.datetime.now())+'''</VALUE>
</PROPERTY>
<PROPERTY NAME="Application" TYPE="string">
	<VALUE>Portal</VALUE>
</PROPERTY>
</INSTANCE>
</VALUE.OBJECT>'''

xml_end_cfg = '''
</DECLGROUP>
</DECLARATION>
</CIM>'''


if 'xml' not in os.listdir(script_path):
	os.mkdir(os.path.join(script_path, 'xml'))
if 'in' not in os.listdir(os.path.join(script_path, 'xml')):
	os.mkdir(os.path.join(script_path, 'xml' , 'in'))
if 'done' not in os.listdir(os.path.join(script_path, 'xml', 'in')):
	os.mkdir(os.path.join(script_path, 'xml' , 'in', 'done'))
if 'out' not in os.listdir(os.path.join(script_path, 'xml')):
	os.mkdir(os.path.join(script_path, 'xml' , 'out'))
if 'done' not in os.listdir(os.path.join(script_path, 'xml', 'out')):
	os.mkdir(os.path.join(script_path, 'xml' , 'out', 'done'))

