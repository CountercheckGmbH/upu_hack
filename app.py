import xml.etree.ElementTree as ET
import json
import requests

def parse_xml_to_dict(file_path):
    tree = ET.parse(file_path)
    root = tree.getroot()

    def extract_fields(element):
        fields = {}

        if len(element) == 0:
            return element.text

        for child in element:
            child_tag = child.tag.replace("{", "").replace(
                "}", "_"
            )  # Replace curly braces with underscores
            if child_tag in fields:
                if isinstance(fields[child_tag], list):
                    fields[child_tag].append(extract_fields(child))
                else:
                    fields[child_tag] = [fields[child_tag], extract_fields(child)]
            else:
                fields[child_tag] = extract_fields(child)

        return fields

    fields_dict = extract_fields(root)
    return fields_dict


def send_request(itmatt_data):
    url = "COUNTERCHECK/itmatt"
    
    files = {
        # 'image': open(image_path, 'rb'),
        "info": (None, json.dumps(itmatt_data))
    }

    response = requests.put(url, files=files)

    res_dict = json.loads(response.text)
    
    for one_result in res_dict.get("results",{}):

        for one in one_result.get("classifyResults", {}):
            if one.get("className", "NA") == "Counterfeit":
                print(one.get("className", "NA") + ":" + str(one.get("confidence", "NA")))


if __name__ == "__main__":

    xml_file_path = "./upuEdiMessagingXmlSchemasAndExamplesEn/m33-11_itmatt_1_5_0_example.xml"

    fields_dict = parse_xml_to_dict(xml_file_path)

    #! DEBUG
    # output_file_path = "./m33-11_itmatt_1_5_0_example.json"
    # with open(output_file_path, "w") as json_file:
    #     json.dump(fields_dict, json_file, indent=4)
    # 
    # print(f"JSON data saved to {output_file_path}")

    if fields_dict and fields_dict.get("m33_message", {}).get("m33_msgbody", {}).get(
        "m33_itmatt_1_5_0", {}
    ).get("m33_item"):
        records = (
            fields_dict.get("m33_message", {})
            .get("m33_msgbody", {})
            .get("m33_itmatt_1_5_0", {})
            .get("m33_item")
        )
        print("Number of itmatt records: " + str(len(records)))
        for i, one_itmatt in enumerate(records):
            print("Processing itmatt #" + str(i))
            send_request(itmatt_data=one_itmatt)