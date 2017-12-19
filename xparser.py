# -*- coding: utf-8 -*-
from config_file import *
import os, time
import xml.etree.ElementTree as ET
from db import makeQuery

all_calls = []
xml_id_counter = 0

class Processing:
	
	def get_file_list(self):
		file_list = file_list_result = []
		file_list = os.listdir(xml_path_inb)
		for filename in os.listdir(xml_path_inb):
			fullname = os.path.join(xml_path_inb, filename)
			#ignore and delete empty files
			if os.path.getsize(fullname) == 0:
				self.move_xml_to_done(fullname,xml_done_path_inb)
				continue 
			#only xml files
			if not filename.endswith('.xml'): continue
			file_list_result.append(fullname)
		return file_list_result

	def create_call_list_from_xml(self,file_list):
		for filename in file_list:
			print('new file',filename)
			tree = ET.parse(filename)	
			# get root element
			root = tree.getroot()
			# iterate news instances
			for instance in root.findall('./DECLARATION/DECLGROUP/VALUE.OBJECT//INSTANCE'):
				properties_dict = {}
				properties_dict["CLASSNAME"] = instance.attrib['CLASSNAME']
				for child in instance:
					for property in child:
						properties_dict[child.attrib['NAME']] = property.text.replace("\"","")
				# print('prop dict',properties_dict)
				all_calls.append(properties_dict)
			if move_processed_xmls_cfg == 1:
				self.move_xml_to_done(filename,xml_done_path_inb)
		return all_calls

	def create_xml_for_instance(self,data_dict,sber_id):
		print ('NUM - ',data_dict['sb_id'])
		text_done = text_reject = ''
		text = '''
	<VALUE.OBJECT>
	<INSTANCE CLASSNAME="%(classname)s">
	<PROPERTY NAME="ID" TYPE="string">
		<VALUE>%(counter)s</VALUE>
	</PROPERTY>
	<PROPERTY NAME="СБ_ID" TYPE="string">
		<VALUE>%(sb_id)s</VALUE>
	</PROPERTY>
	<PROPERTY NAME="ИДЕНТИФИКАТОР" TYPE="string">
		<VALUE>%(prefix)s%(id)s</VALUE>
	</PROPERTY>''' % {'classname': classname_status_dict[str(data_dict['status'])], 'counter': self.increment(), 'id': data_dict['id'], 'sb_id':data_dict['sb_id'], 'prefix':id_prefix}

		if data_dict['status'] == 7:
			text_done = '''
	<PROPERTY NAME="РЕШЕНИЕ" TYPE="string">
		<VALUE>%(solution)s</VALUE>
	</PROPERTY>
	<PROPERTY NAME="КОД_ЗАКРЫТИЯ" TYPE="string">
		<VALUE>%(closure_code)s</VALUE>
	</PROPERTY>
	<PROPERTY NAME="СТАТУС" TYPE="string">
		<VALUE>2</VALUE>
	</PROPERTY>''' % {'solution': data_dict['solution'], 'closure_code': data_dict['closure_code']}

		if data_dict['status'] == 8:
			text_done = '''
	<PROPERTY NAME="РЕШЕНИЕ" TYPE="string">
		<VALUE>%(solution)s</VALUE>
	</PROPERTY>
	<PROPERTY NAME="КОД_ЗАКРЫТИЯ" TYPE="string">
		<VALUE>4</VALUE>
	</PROPERTY>
	<PROPERTY NAME="СТАТУС" TYPE="string">
		<VALUE>8</VALUE>
	</PROPERTY>''' % {'solution': data_dict['solution']}

		text_end = '''
	</INSTANCE>
	</VALUE.OBJECT>	'''
		text = text + text_done + text_end

		# print(text)
		return text

	def add_xml_headers(self,xmltext):
		xml_final = xml_start_cfg + xmltext + xml_end_cfg
		return xml_final

	def write_to_file(self,xmltext):
		file_path = os.path.join(xml_path_outb,xml_out_name_cfg)
		fh = open(file_path, 'wb')
		fh.write(xmltext.encode('utf-8'))

	def get_sd_ids(self,calls):
		sd_ids = []
		for call in calls:
			for prop,value in call.items():
				if prop == 'СБ_ID' and value not in sd_ids:
					sd_ids.append(value)
		return sd_ids
		
	def make_req_tuple(self,call):
		type = req_data = ''
		if call['CLASSNAME']=='NEW':
			type = 'insert'
			template = call['ШАБЛОН']
			sb_id = call['СБ_ID']
			short_descr = call['ТЕМА']
			descr = call['ИНФОРМАЦИЯ']
			caller = call['ИНИЦИАТОР']
			phone = call['ТЕЛЕФОН']
			sber_wg = call['РГ']
			# sberassignee = call['ИСПОЛНИТЕЛЬ']
			srok_time = str(local.localize(datetime.datetime.strptime (call['СРОК'], "%Y.%m.%d %H:%M:%S"), is_dst=None).timestamp())
			print('srok time -',srok_time)

			# Опеределим какая компания и РГ по РГ банка
			get_ids_select = """SELECT company.id as comp, workgroups.id as grp from company 
			INNER JOIN `companytowg` on company.id = companytowg.company_id
			INNER JOIN `bankwg` on bankwg.id = companytowg.bank_wg_id
			INNER JOIN `workgroups` on workgroups.id = companytowg.wg_id
			where bankwg.wg_name = \'"""
			get_ids = makeQuery('select', get_ids_select + sber_wg + "\'")
			company_id = str(get_ids["comp"])
			workgroup_id = str(get_ids["grp"])

			desired_time = '0'
			if (call['ЖЕЛАЕМАЯ_ДАТА'] != '.. ::'):
					desired_time = str(local.localize(datetime.datetime.strptime (call['ЖЕЛАЕМАЯ_ДАТА'], "%Y.%m.%d %H:%M:%S"), is_dst=None).timestamp())

			reg_time = str(local.localize(datetime.datetime.strptime (call['ВРЕМЯ_РЕГИСТРАЦИИ'], "%Y.%m.%d %H:%M:%S"), is_dst=None).timestamp())

			req_data = "INSERT INTO `requests` (`sb_id`, `status`, `descr`, `full_descr`, `date_created_sber`, `date_deadline`, `date_desired`, `sberwg`, `bank_contact`, `bank_contact_phone`, `company_id`, `workgroup_id`) VALUES (\'"+sb_id+"\', 2, \'"+short_descr+"\', \'"+descr+"\', "+reg_time+", \'"+srok_time+"\', \'"+desired_time+"\', \'"+ sber_wg +"\', \'"+ caller + "\', \'"+phone +"\',"+company_id+","+workgroup_id+")"
			req_data = req_data.replace('\r\n', "\n")
			return type,req_data,sb_id
			
		if call['CLASSNAME']=='REJECT':
			type = 'update'
			sb_id = call['СБ_ID']
			req_data = "UPDATE `requests` SET `status` = 8, `closure_code` = 3, `solution`= 'Отозвано клиентом из банка' WHERE `sb_id` = \'" + sb_id + "\'"
			req_data = req_data.replace('\r\n', "\n")
			return type,req_data,sb_id
		else:
			return None,None,None
			
	def delete_file(self,file):
		os.remove(file)
		print (file, "have been deleted")
		
	def move_xml_to_done(self,source,destination):
		destination_with_xml = os.path.join(destination, os.path.basename(source))
		print ("moving",source,"to",destination_with_xml)
		os.replace(source, destination_with_xml)

	def file_exist(self,file_path):
		return os.path.isfile(file_path)


	def increment(self):
		global xml_id_counter
		xml_id_counter += 1
		return xml_id_counter
