import json
import os

xml_files_path = r"props/xml_files/"

DATABASES = {
    "p51vms": {
        "engine": "mysql+mysqldb",
        "user": "dbuser",
        "password": "dbpassword",
        "host": "p51vms",
        "port": 3306,
        "database": "s11semd",
        "charset": "utf8",
        "IEMK_ORG_ID": 3196,
        "B15_MODE": False,
    }
}

DATABASE_CONFIG = DATABASES["p51vms"]

namespaces = {
    'PII': 'urn:hl7-ru:PII',
    'address': 'urn:hl7-ru:address',
    'f103': 'urn:f103',
    'f88': 'urn:f88',
    'fias': 'urn:hl7-ru:fias',
    'identity': 'urn:hl7-ru:identity',
    'medService': 'urn:hl7-ru:medService',
    'ns': 'urn:hl7-org:v3',
    'tmk': 'urn:tmk'
}

xpath_comment = "/preceding-sibling::comment()[1]"

# Определение базовых значений заголовков с регулярными выражениями для валидации
# headers_base_value = {
#     "ns:ClinicalDocument/ns:id[1]": {
#         "root": {
#             "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.51$",
#         },
#         "extension": {"@type": r"\d+"},
#     },
#     "ns:ClinicalDocument/ns:setId": {
#         "root": {
#             "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.50$",
#         },
#         "extension": {"@type": r"\d+"},
#     },
#     "ns:ClinicalDocument/ns:versionNumber": {"value": {"@type": r"\d+"}},
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[1]": {
#         "root": {
#             "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.10$",
#         },
#         "extension": {"@type": r"\d+"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[2]": {
#         "root": {
#             "@type": r"^.+$",
#         },
#         "extension": {"@type": r"\d+"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IdentityCardType": {
#         "code": {"@type": "^.+$"},
#         "displayName": {"@type": "^.+$"},
#         "codeSystemVersion": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Series": {
#         "text": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Number": {
#         "text": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgName": {
#         "text": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgCode": {
#         "text": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueDate": {
#         "value": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:InsurancePolicyType": {
#         "code": {"@type": "^.+$"},
#         "displayName": {"@type": "^.+$"},
#         "codeSystemVersion": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:Number": {
#         "text": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:Type": {
#         "code": {
#             "@type": "^.+$",
#         },
#         "displayName": {"@type": "^.+$"},
#         "codeSystemVersion": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:streetAddressLine": {
#         "text": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:stateCode": {
#         "code": {"@type": "^.+$"},
#         "displayName": {"@type": "^.+$"},
#         "codeSystemVersion": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:residentCode": {
#         "code": {"@type": "^.+$"},
#         "displayName": {"@type": "^.+$"},
#         "codeSystemVersion": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:postalCode": {
#         "text": {"@type": "^.+$"}
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:AOGUID": {
#         "text": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:HOUSEGUID": {
#         "text": {"@type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:telecom": {
#         "use": {"type": "^.+$"},
#         "value": {"type": "^tel:\+\d{11}$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:patient/ns:name/ns:family": {
#         "text": {"type": "^.+$"},
#     },
#     "ns:ClinicalDocument/ns:recordTarget[1]/ns:patientRole/ns:patient/ns:name/ns:given": {
#         "text": {"@type": "^.+$"},
#     },
# }

with open("props/base_headers_values.json", 'r', encoding='utf-8') as f:
    headers_base_value = json.loads(f.read())


semd_paths = {semd: xml_files_path + semd + semd_path for semd, semd_path in map(lambda file: os.path.splitext(file), filter(lambda file: file.endswith(".xml"), os.listdir(xml_files_path)))}
