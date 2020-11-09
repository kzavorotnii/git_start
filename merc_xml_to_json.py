import glob
import os
import xml.etree.ElementTree as ET
from tqdm import tqdm
from datetime import datetime

start_time = datetime.now()
file = (glob.glob("*preOutgoingConsignmentRequest_out.xml"))
for i in tqdm(file):
    pass
for xml in file:
    context = ET.iterparse(xml, events=("end", "start", "start-ns"))
    ns = {}
    cod_gp = []
    for event, element in context:
        if event == "start-ns":
            ns[element[0]] = element[1]
        else:
            break
    # print(xml)
    # print("1) Create NS")

    for event, element in context:
        if event == "start" and element.tag == "{" + ns['vd'] + "}vetCertificate":
            cod_gp.append(str(element.attrib).replace("{'for': ", "").replace("'", "").replace("}", ""))
    # print("2) PART_OTG_2P is ready")

    json_file = xml.replace(".xml", ".json")
    mode = "w"
    Counter0 = 0
    x = 0
    f = open(json_file, mode, encoding='utf-8')
    f.write('{\n\t "table": {\n\t "tabledate": [ \n\t  {\n\t "name": "disp_otgn.otg_2p", \n\t "data":[\n')
    mode = "a"
    context = ET.iterparse(xml, events=("end", "start"))
    for event, element in context:
        if event == "start" and element.tag == "{" + ns['vd'] + "}consignment":
            if Counter0 == 0:
                f.write(str(element.attrib).replace("{", "\t {\n\t ").replace("'", '"').replace('}', ',') + '\n')
            if Counter0 != 0:
                with open(json_file, mode) as f:
                    f.write("\t },\n" + str(element.attrib).
                            replace("{", "\t {\n\t ").replace("'", '"').replace('}', ',') + '\n')
        if event == "start" and element.tag == "{" + ns['vd'] + "}volume":
            with open(json_file, mode) as f:
                f.write('\t "netto": "' + str(element.text) + '",\n')
        if event == "start" and element.tag == "{" + ns['dt'] + "}quantity":
            if Counter0 % 2 == 0:
                with open(json_file, mode) as f:
                    f.write('\t "cnt_u": "' + str(element.text) + '",\n')
        if event == "end" and element.tag == "{" + ns['dt'] + "}productMarks":
            if str(element.attrib) == "{'class': 'BN'}":
                with open(json_file, mode) as f:
                    f.write('\t "batchid": "' + str(element.text) + '",\n')
        if event == "start" and element.tag == "{" + ns['dt'] + "}quantity":
            if Counter0 % 2 != 0:
                with open(json_file, mode) as f:
                    f.write('\t "cnt_f": "' + str(element.text) + '",\n')
            Counter0 += 1
        if event == "start" and element.tag == "{" + ns['vd'] + "}sourceStockEntry":

            for ev, elem in context:
                with open(json_file, mode) as f:
                    f.write('\t "stock_guid": ' + '"' + str(elem.text) + '",\n')
                    f.write('\t "cod_gp": "' + str(cod_gp[x]) + '"\n')
                x += 1
                break
    f = open(json_file, mode, encoding='utf-8')
    f.write("\t}\n\t ]\n\t  },\n")
    # print("3) OTG_2P is ready")

    f.write('\t{\n\t"name": "s_gpr_merc",\n\t"data":[\n')
    counter = 0
    context = ET.iterparse(xml, events=("end", "start"))
    for event, element in context:
        if event == "start" and element.tag == "{" + ns['vd'] + "}productItem":
            for i in element:
                if i.tag == "{" + ns['bs'] + "}guid" and counter == 0:
                    f.write('\t{\n\t"pi_guid": "' + str(i.text) + '",\n')
                if i.tag == "{" + ns['bs'] + "}guid" and counter != 0:
                    f.write('\t},\n\t{\n\t"pi_guid": "' + str(i.text) + '",\n')
        if event == "start" and element.tag == "{" + ns['vd'] + "}unit":
            for i in element:
                if i.tag == "{" + ns['bs'] + "}guid":
                    f.write('\t"pi_un_guid": "' + str(i.text) + '",\n')
        if event == "start" and element.tag == "{" + ns['dt'] + "}package":
            for el in element:
                if el.tag == "{" + ns['dt'] + "}packingType":
                    for i in el:
                        if counter % 2 == 0:
                            f.write('\t"l4_pt_guid": "' + str(i.text) + '",\n')
                        else:
                            f.write('\t"l2_pt_guid": "' + str(i.text) + '"\n')
                        counter += 1
    f.write('\t}\n\t ]\n\t  },\n')
    # print('4) S_GPR_MERC is ready')

    f = open(json_file, mode, encoding='utf-8')
    f.write('\t{\n\t"name": "s_gpr",\n\t"data":[\n')
    counter = 0
    context = ET.iterparse(xml, events=("end", "start"))
    for event, element in context:
        if event == 'start' and element.tag == "{" + ns['dt'] + "}name" and counter == 0:
            f.write('\t{\n\t"name_gp": "' + str(element.text) + '",\n')
        if event == 'start' and element.tag == "{" + ns['dt'] + "}name" and counter != 0:
            f.write('\t},\n\t{\n\t"name_gp": "' + str(element.text) + '",\n')
        if event == 'start' and element.attrib == {'class': 'EAN13'}:
            if counter % 2 == 0:
                f.write('\t"shtx_cc": "' + str(element.text) + '",\n')
            else:
                f.write('\t"shtx": "' + str(element.text) + '"\n')
            counter += 1
    f.write('\t}\n\t ]\n\t  },\n\t')
    # print('5) S_GPR is ready')

    f = open(json_file, mode, encoding='utf-8')
    context = ET.iterparse(xml, events=("end", "start"))
    for event, element in context:
        if event == "start" and element.tag == "{" + ns['merc'] + "}localTransactionId":
            f.write('{\n\t"name": "cex_otgn.gov_work",\n\t"data":[\n\t{\n\t"vn_gov": "' + str(
                element.text) + '"\n\t}\n\t ]\n\t  },\n')
        if event == "start" and element.tag == "{" + ns['vd'] + "}vehicleNumber":
            f.write('\t{\n\t"name": "cex_otgn.otg_0",\n\t"data":[\n\t{\n\t"gosn": "' + str(
                element.text) + '"\n\t}\n\t ]\n\t  },\n')
        if event == "start" and element.tag == "{" + ns['vd'] + "}waybill":
            for el in element:
                if el.tag == "{" + ns['vd'] + "}issueNumber":
                    f.write('\t{\n\t"name": "cex_otgn.otg_1",\n\t"data":[\n\t{\n\t"num_ttn": "' + str(
                        el.text) + '"\n\t}\n\t ]\n\t  }\n\t ]\n\t }\n}')
    # print("6) HEADING si ready")
    f.close()
    os.remove(xml)
print(datetime.now() - start_time)
