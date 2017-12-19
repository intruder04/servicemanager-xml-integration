# -*- coding: utf-8 -*-
from config_file import *
from mail import SendMail 
from mail import GetMail
from xparser import Processing
from db import makeQuery
import os

# Получение почты от банка
GetMail().recieve_mail()

# Обработка входящих xml
process_xmls = Processing()

# список входящих файлов
xml_file_list = process_xmls.get_file_list()
print('file list -',xml_file_list)
# xml_file_list = ['/Users/intruder04/Sites/mamp/portal/integration/expl/oktava/xml/in/to_oktava.xml21-15-01-15.08.2017.xml']

# парсинг данных из xml
calls_list = process_xmls.create_call_list_from_xml(xml_file_list)

# только айдишники заявок
sd_ids = process_xmls.get_sd_ids(calls_list)

for call in calls_list:
	req_tuple = process_xmls.make_req_tuple(call)
	# print ('reqstring',req_tuple, req_tuple[0])
	if (req_tuple[0] == 'insert'):
    	# проверка существования заявки. Если нет - создание
			check_if_exist = makeQuery("select","SELECT sb_id from requests where sb_id = \'"+req_tuple[2]+"\'")
			if check_if_exist is None:
				print ("Call ",req_tuple[2],"doesnt exist, CREATE!")
				makeQuery("insert",req_tuple[1])
			else:
				print("Call ",req_tuple[2],"already exists, ignoring")

# ==========================
# Отправка ответа в банк
print ("have to create xml for:", sd_ids)
xml_instances = ''
for call in sd_ids:
	queryres = makeQuery("select","SELECT id, sb_id, solution, status, closure_code, date_done from requests where sb_id = \'"+call+"\'")
	# Создаем xml только по тем заявкам, которые есть в БД
	if queryres is not None:
		xml_instance = process_xmls.create_xml_for_instance(queryres,call)
		xml_instances = xml_instances + xml_instance

# запись xml для отправки в файл
final_outb_xml = process_xmls.add_xml_headers(xml_instances)
process_xmls.write_to_file(final_outb_xml)


# отправка письма
if process_xmls.file_exist(outbound_xml_cfg):
	MailObjSend = SendMail(mail_subject, '-', mail_sber_email, outbound_xml_cfg)
	MailObjSend.send_email(MailObjSend.compose_email())

	os.replace(os.path.join(xml_path_outb,xml_out_name_cfg), os.path.join(xml_done_path_outb,xml_out_name_cfg))

#чистка старых XML чтобы не перелимитить inodes
files = os.listdir(xml_path_inb)

for item in files:
	if item.endswith(".xml") and os.stat(os.path.join(xml_path_inb,item)).st_mtime < now - 60 * 86400:
		os.remove(join(xml_path_inb, item))
		print('old file',item,'has been deleted')
