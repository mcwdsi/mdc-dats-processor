import os
import glob
import json
import csv
import urllib.parse
import urllib.request
import urllib.error

dir_name = input("Which directory would you like to check? [data formats], [datasets], [both] ")


if dir_name == "datasets":
    current_dir = os.listdir(".")

    for sub_dir in current_dir:
        if "dats-info" in sub_dir:
            sub_dir = sub_dir + "/*"
            file_list = glob.glob(sub_dir)
            latest_f = max(file_list, key=os.path.getmtime)

            with open(latest_f, encoding="latin-1") as t_name:
                reader = csv.DictReader(t_name, dialect="excel-tab")
                print("Pulling information from ", sub_dir, "...")

                for row in reader:
                    try:
                        id_stored = row["datasetIdentifier"]
                        if id_stored == "identifier will be created at time of release" : continue
                        formatted_id = urllib.parse.quote(id_stored, safe="")
                        metadata_api_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/metadata?identifier="
                        header = {"Accept": "application/json"}
                        url = metadata_api_url + formatted_id

                        r = urllib.request.Request(url, headers=header)
                        rhand = urllib.request.urlopen(r)
                        convert_to_string = rhand.read().decode("latin-1")
                        data = json.loads(convert_to_string)

                        # Check identifier
                        try:
                            id_json = data["identifier"]["identifier"]

                            if id_json != id_stored:
                                print("identifier_current: ", id_json, " /// ",
                                      "identifier_stored: ", id_stored, " /// ")
                        except KeyError:
                            print("Identifier ", id_stored, " not found.")

                        # Check title
                        try:
                            title_json = data["title"]
                            title_stored = row["title"]

                            if title_json != title_stored:
                                print("title_current: ", title_json, " /// ",
                                      "title_stored: ", title_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Title not found for ", id_stored)

                        # Check description
                        try:
                            description_json = data["description"]
                            description_stored = row["description"]

                            if description_json != description_stored:
                                print("description_current: ", description_json, " /// ",
                                      "description_stored: ", description_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Description not found for ", id_stored)

                        # Check disease name
                        try:
                            disease_json = ""
                            for attr in data["isAbout"]:
                                if attr["identifier"]["identifierSource"] == "https://biosharing.org/bsg-s000098":
                                    disease_json = attr["name"]
                            if not disease_json:
                                disease_json = "null"

                            disease_stored = row["disease"]

                            if not disease_stored:
                                disease_stored = "null"

                            if disease_json != disease_stored:
                                print("disease_name_current: ", disease_json, " /// ",
                                      "disease_name_stored: ", disease_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Disease name not found for ", id_stored)

                        # Check authors
                        try:
                            author_list = list()
                            authors_json = ""
                            authors_stored = row["authors"]
                            s = ", "

                            for a in data["creators"]:
                                last = a["lastName"]
                                first = a["firstName"]

                                if last or first:
                                    full_name = first + " " + last
                                    author_list.append(full_name)

                            if not author_list:
                                authors_json = "null"
                            else:
                                authors_json = s.join(author_list)

                                if authors_json != authors_stored:
                                    print("authors_current: ", authors_json, " /// ",
                                          "authors_stored: ", authors_stored, " /// ",
                                          "identifier: ", id_stored)
                        except KeyError:
                            print("Author list not found for ", id_stored)

                        # Check dates created, modified, and accessed
                        try:
                            created_json = ""
                            modified_json = ""
                            accessed_json = ""
                            created_stored = row["created"]
                            modified_stored = row["modified"]
                            accessed_stored = row["accessed"]

                            for d in data["distributions"]:
                                if not d["dates"]:
                                    created_json = "null"
                                    modified_json = "null"
                                    accessed_json = "null"
                                else:
                                    for e in d["dates"]:
                                        if e["type"]["value"] == "creation":
                                            created_json = e["date"]
                                        if e["type"]["value"] == "modified":
                                            modified_json = e["date"]
                                        if e["type"]["value"] == "accessed":
                                            accessed_json = e["date"]

                            if not created_json:
                                created_json = "null"
                            if not modified_json:
                                modified_json = "null"
                            if not accessed_json:
                                accessed_json = "null"

                            if created_json != created_stored:
                                print("created_date_current:", created_json, "///",
                                      "created_date_stored:", created_stored, "///",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("Creation, modification, and access dates not found for ", id_stored)

                        # Check landing page
                        try:
                            landing_page_json = data["distributions"][0]["access"]["landingPage"]
                            landing_page_stored = row["landingPage"]

                            if landing_page_json != landing_page_stored:
                                print("landing_page_current:", landing_page_json, " /// ",
                                      "landing_page_stored:", landing_page_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("Landing page not found for ", id_stored)

                        # Check access page
                        try:
                            access_page_json = data["distributions"][0]["access"]["accessURL"]
                            access_page_stored = row["accessPage"]

                            if access_page_json != access_page_stored:
                                print("access_page_current:", access_page_json, " /// ",
                                      "access_page_stored:", access_page_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("Access page not found for ", id_stored)

                        # Check format
                        try:
                            s = ", "
                            format_json = s.join(data["distributions"][0]["formats"])
                            format_stored = row["format"]

                            if not format_json:
                                format_json = "null"

                            if format_json != format_stored:
                                print("format_current:", format_json, " /// ",
                                      "format_stored:", format_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            if format_stored == "null":
                                format_json = "null"
                            elif format_json == format_stored : continue
                            else:
                                print("Format(s) not found for ", id_stored)

                        # Check schema
                        try:
                            schema_json = data["distributions"][0]["conformsTo"][0]["name"]
                            schema_stored = row["conformsTo"]

                            if schema_json != schema_stored:
                                print("schema_current:", schema_json, " /// ",
                                      "schema_stored:", schema_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("Schema not found for ", id_stored)

                        # Check license
                        try:
                            license_json = ""
                            license_stored = row["license"]

                            if not data["licenses"]:
                                license_json = "null"
                            else:
                                for license in data["licenses"]:
                                    if not license["name"]:
                                        license_json = "null"
                                    else:
                                        license_json = license["name"]

                            if license_json != license_stored:
                                print("liense_current:", license_json, " /// ",
                                      "license_stored:", license_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            if license_stored == "null":
                                license_json = "null"
                            else:
                                print("License not found for ", id_stored)

                        # Check geography
                        try:
                            geo_lst = list()
                            geo_json = ""
                            geo_stored = row["geography"]
                            s = ", "

                            if not data["spatialCoverage"]:
                                geo_json = "null"

                            for region in data["spatialCoverage"]:
                                if not region["name"] : continue
                                else:
                                    geo_lst.append(region["name"])

                            if not geo_lst:
                                geo_json = "null"
                            else:
                                geo_json = s.join(geo_lst)

                            if geo_json != geo_stored:
                                print("geo_current:", geo_json, " /// ",
                                      "geo_stored:", geo_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("Geographical regions not found for ", id_stored)

                        # Check Apollo location code
                        alc_json = ""
                        alc_stored = row["apolloLocationCode"]

                        if not data["spatialCoverage"]:
                            alc_json = "null"
                        else:
                            for s in data["spatialCoverage"]:
                                if not s["identifier"]:
                                    alc_json = "null"
                                elif not s["identifier"]["identifier"]:
                                    alc_json = "null"
                                else:
                                    alc_json = s["identifier"]["identifier"]

                        if alc_json != alc_stored:
                            print("apollo_location_code_current:", alc_json, " /// ",
                                  "apollo_location_code_stored:", alc_stored, " /// ",
                                  "identifier:", id_stored)

                        # Check ISO location codes
                        try:
                            iso3166_json = ""
                            iso3166_1_json = ""
                            iso3166a3_json = ""
                            iso3166_stored = row["ISO_3166"]
                            iso3166_1_stored = row["ISO_3166-1"]
                            iso3166a3_stored = row["ISO_3166-1_alpha-3"]

                            if not data["spatialCoverage"]:
                                iso3166a3_json = "null"
                                iso3166_1_json = "null"
                                iso3166_json = "null"
                            else:
                                for identifier in data["spatialCoverage"]:
                                    if not identifier["alternateIdentifiers"]:
                                        iso3166a3_json = "null"
                                        iso3166_1_json = "null"
                                        iso3166_json = "null"
                                    else:
                                        for code in identifier["alternateIdentifiers"]:
                                            if code["identifierSource"] == "ISO 3166-1 alpha-3":
                                                iso3166a3_json = code["identifier"]
                                            if code["identifierSource"] == "ISO 3166-1":
                                                iso3166_1_json = code["identifier"]
                                            if code["identifierSource"] == "ISO 3166":
                                                iso3166_json = code["identifier"]

                                    if not iso3166a3_json:
                                        iso3166a3_json = "null"
                                    if not iso3166_1_json:
                                        iso3166_1_json = "null"
                                    if not iso3166_json:
                                        iso3166_json = "null"

                            if iso3166a3_json != iso3166a3_stored:
                                print("iso_3166_1_alpha_3_current:", iso3166a3_json, " /// ",
                                      "iso_3166_1_alpha_3_stored:", iso3166a3_stored, " /// ",
                                      "identifier:", id_stored)
                            if iso3166_1_json != iso3166_1_stored:
                                print("iso_3166_1_current:", iso3166_1_json, " /// ",
                                      "iso_3166_1_stored:", iso3166_1_stored, " /// ",
                                      "identifier:", id_stored)
                            if iso3166_json != iso3166_stored:
                                print("iso_3166_current:", iso3166_json, " /// ",
                                      "iso_3166_stored:", iso3166_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            print("ISO-3166, ISO3166-1, and ISO-3166-1 alpha-3 codes not found for: ", id_stored)


                    except : continue

if dir_name == "data formats":
    current_dir = os.listdir(".")

    for sub_dir in current_dir:
        if "data-formats" in sub_dir:
            sub_dir = sub_dir + "/*"
            file_list = glob.glob(sub_dir)
            latest_f = max(file_list, key=os.path.getmtime)

            with open(latest_f) as t_name:
                reader = csv.DictReader(t_name, dialect="excel-tab")
                print("Pulling information from data-formats-info/...")

                for row in reader:
                    try:
                        id_stored = row["identifier"]
                        formatted_id = urllib.parse.quote(id_stored, safe="")
                        metadata_api_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/metadata?identifier="
                        header = {"Accept": "application/json"}
                        url = metadata_api_url + formatted_id

                        r = urllib.request.Request(url, headers=header)
                        rhand = urllib.request.urlopen(r)
                        convert_to_string = rhand.read().decode("latin-1")
                        data = json.loads(convert_to_string)

                        # Check identifier
                        try:
                            id_json = data["identifier"]["identifier"]

                            if id_json != id_stored:
                                print("identifier_current: ", id_json, " /// ",
                                      "identifier_stored: ", id_stored, " /// ")
                        except KeyError:
                            print("Identifier", id_stored, " not found.")

                        # Check name
                        name_json = data["name"]
                        name_stored = row["name"]

                        if name_json != name_stored:
                            print("name_current:", name_json, " /// ",
                                  "name_stored:", name_stored, " /// ",
                                  "identifier:", id_stored)

                        # Check identifier source
                        try:
                            id_source_json = data["identifier"]["identifierSource"]
                            id_source_stored = row["identifier_source"]

                            if id_source_json != id_source_stored:
                                print("identifier_source_current: ", id_source_json, " /// ",
                                      "identifier_source_stored:", id_source_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Identifier source not found for ", id_stored)

                        # Check type
                        try:
                            type_json = data["type"]["value"]
                            type_stored = row["type"]

                            if not type_json:
                                type_json = "null"

                            if type_json != type_stored:
                                print("type_current: ", type_json, " /// ",
                                      "type_stored: ", type_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Type not found for ", id_stored)

                        # Check type_IRI
                        try:
                            type_iri_json = data["type"]["valueIRI"]
                            type_iri_stored = row["type_IRI"]

                            if not type_iri_json:
                                type_iri_json = "null"

                            if type_iri_json != type_iri_stored:
                                print("type_IRI_current: ", type_iri_json, " /// ",
                                      "type_IRI_stored: ", type_iri_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Type IRI not found for ", id_stored)

                        # Check description
                        try:
                            description_json = data["description"]
                            description_stored = row["description"]

                            if description_json != description_stored:
                                print("description_current: ", description_json, " /// ",
                                      "description_stored: ", description_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Description not found for ", id_stored)

                        # Check licenses
                        try:
                            license_json = ""
                            license_stored = row["licenses"]

                            if not data["licenses"]:
                                license_json = "null"
                            else:
                                for license in data["licenses"]:
                                    if not license["name"]:
                                        license_json = "null"
                                    else:
                                        license_json = license["name"]

                            if license_json != license_stored:
                                print("liense_current:", license_json, " /// ",
                                      "license_stored:", license_stored, " /// ",
                                      "identifier:", id_stored)
                        except KeyError:
                            if license_stored == "null":
                                license_json = "null"
                            else:
                                print("License not found for ", id_stored)

                        # Check version
                        try:
                            version_json = data["version"]
                            version_stored = row["version"]

                            if not version_json:
                                version_json = "null"

                            if version_json != version_stored:
                                print("version_current: ", version_json, " /// ",
                                      "version_stored: ", version_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Version not found for ", id_stored)

                        # Check human_readable_data_format_specification_value
                        try:
                            extra_properties = data["extraProperties"]

                            human_readable_value_stored = row["human-readable_data_format_specification_value"]
                            human_readable_value_iri_stored = row["human-readable_data_format_specification_value_IRI"]
                            machine_readable_value_stored = row["machine-readable_data_format_specification_value"]
                            machine_readable_value_iri_stored = row["machine-readable_data_format_specification_value_IRI"]

                            human_readable_value_json = ""
                            human_readable_value_iri_json = ""
                            machine_readable_value_json = ""
                            machine_readable_value_iri_json = ""

                            if extra_properties:
                                for property in extra_properties:
                                    if "human" in property["category"]:
                                        human_readable_value_json = property["values"][0]["value"]
                                        human_readable_value__iri_json = property["values"][0]["valueIRI"]
                                    if "machine" in property["category"]:
                                        machine_readable_value_json = property["values"][0]["value"]
                                        machine_readable_value_iri_json = property["values"][0]["valueIRI"]

                            if not human_readable_value_json:
                                human_readable_value_json = "null"
                            if not human_readable_value_iri_json:
                                human_readable_value_iri_json = "null"
                            if not machine_readable_value_json:
                                machine_readable_value_json = "null"
                            if not machine_readable_value_iri_json:
                                machine_readable_value_iri_json = "null"

                            if human_readable_value_json != human_readable_value_stored:
                                print("human_readable_value_current: ", human_readable_value_json, " /// ",
                                      "human_readable_value_stored: ", human_readable_value_stored, " /// ",
                                      "identifier: ", id_stored)
                            if human_readable_value_iri_json != human_readable_value_iri_stored:
                                print("human_readable_value_iri_current: ", human_readable_value_iri_json, " /// ",
                                      "human_readable_value_iri_stored: ", human_readable_value_iri_stored, " /// ",
                                      "identifier: ", id_stored)
                            if machine_readable_value_json != machine_readable_value_stored:
                                print("machine_readable_value_current: ", machine_readable_value_json, " /// ",
                                      "machine_readable_value_stored: ", machine_readable_value_stored, " /// ",
                                      "identifier: ", id_stored)
                            if machine_readable_value_iri_json != machine_readable_value_iri_stored:
                                print("machine_readable_value_iri_current: ", machine_readable_value_iri_json, " /// ",
                                      "machine_readable_value_iri_stored: ", machine_readable_value_iri_stored, " /// ",
                                      "identifier: ", id_stored)
                        except KeyError:
                            print("Human- and machine-readable data format value specifications not found for ", id_stored)


                    except urllib.error.HTTPError:
                        print("404 not found for ", id_stored)