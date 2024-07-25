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
    "ns": "urn:hl7-org:v3",
    "identity": "urn:hl7-ru:identity",
    "address": "urn:hl7-ru:address",
    "fias": "urn:hl7-ru:fias",
}

xpath_comment = "/preceding-sibling::comment()[1]"

# Определение базовых значений заголовков с регулярными выражениями для валидации
headers_base_value = {
    "ns:ClinicalDocument/ns:id[1]": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.51$",
        },
        "extension": {"@type": r"\d+"},
    },
    "ns:ClinicalDocument/ns:setId": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.50$",
        },
        "extension": {"@type": r"\d+"},
    },
    "ns:ClinicalDocument/ns:versionNumber": {"value": {"@type": r"\d+"}},
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[1]": {
        "root": {
            "@type": r"^[0-2](\.([1-9][0-9]*|0))+\.100([.]([1-9][0-9]*|0))+\.10$",
        },
        "extension": {"@type": r"\d+"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:id[2]": {
        "root": {
            "@type": r"^.+$",
        },
        "extension": {"@type": r"\d+"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IdentityCardType": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Series": {
        "text": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:Number": {
        "text": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgName": {
        "text": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueOrgCode": {
        "text": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:IdentityDoc/identity:IssueDate": {
        "value": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:InsurancePolicyType": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/identity:InsurancePolicy/identity:Number": {
        "text": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:Type": {
        "code": {
            "@type": "^.+$",
        },
        "displayName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:streetAddressLine": {
        "text": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:stateCode": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/address:residentCode": {
        "code": {"@type": "^.+$"},
        "displayName": {"@type": "^.+$"},
        "codeSystemVersion": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/ns:postalCode": {
        "text": {"@type": "^.+$"}
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:AOGUID": {
        "text": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:addr[1]/fias:Address/fias:HOUSEGUID": {
        "text": {"@type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:telecom": {
        "use": {"type": "^.+$"},
        "value": {"type": "^tel:\+\d{11}$"},
    },
    "ns:ClinicalDocument/ns:recordTarget/ns:patientRole/ns:patient/ns:name/ns:family": {
        "text": {"type": "^.+$"},
    },
    "ns:ClinicalDocument/ns:recordTarget[1]/ns:patientRole/ns:patient/ns:name/ns:given": {
        "text": {"@type": "^.+$"},
    },
}


semd_paths = {
    "147": r"props/147.xml",
    "81": r"props/81.xml",
}
