import os
import json
from csv import DictWriter


def parse_authors(jsn):
    author_list = []
    s = ", "

    try:
        for i in jsn["creators"]:
            last = i["lastName"]
            first = i["firstName"]

            str = first + " " + last
            author_list.append(str)

            continue
    except:
        author_list.append("null")

    authors = s.join(author_list)

    return authors


def parse_dates(jsn):
    dates = dict()

    try:
        for element in jsn["distributions"]:
            if not element["dates"]:
                dates["creationDate"] = "null"
                dates["curationDate"] = "null"
                dates["modificationDate"] = "null"
                dates["accessedDate"] = "null"
            else:
                date_lst = []
                for i in element["dates"]:
                    date_lst.append(i["type"]["value"])

                    value = i["type"]["value"]
                    value += "Date"
                    dates[value] = i["date"]

                    if "creation" not in date_lst:
                        dates["creationDate"] = "null"
                    if "modification" not in date_lst:
                        dates["modificationDate"] = "null"
                    if "curation" not in date_lst:
                        dates["curationDate"] = "null"
                    if "accessed" not in date_lst:
                        dates["accessedDate"] = "null"

                    continue
    except:
        dates["creationDate"] = "null"
        dates["curationDate"] = "null"
        dates["modificationDate"] = "null"
        dates["accessedDate"] = "null"

    return dates


def parse_format(jsn):
    try:
        s = ", "

        formats = s.join(jsn["distributions"][0]["formats"])
    except:
        formats = "null"

    return formats


def parse_standard(jsn):
    try:
        standard = jsn["distributions"][0]["conformsTo"][0]["name"]
    except:
        standard = "null"

    return standard


def parse_landing_page(jsn):
    try:
        url = jsn["distributions"][0]["access"]["landingPage"]
    except:
        url = "null"

    return url


def parse_access_page(jsn):
    try:
        url = jsn["distributions"][0]["access"]["accessURL"]
    except:
        url = "null"

    return url

def parse_dataset_id(jsn):
    if jsn["identifier"]["identifier"] == "":
        id = "null"
    else:
        id = jsn["identifier"]["identifier"]

    return id


def parse_geo(jsn):
    regions = []
    s = ", "

    for attr in jsn["spatialCoverage"]:
        regions.append(attr["name"])

        continue

    names = s.join(regions)

    return names


def parse_geo_id(jsn):
    locationCodes = []
    s = ", "

    for attr in jsn["spatialCoverage"]:
        str = attr["identifier"]["identifier"]

        if "http" in str:
            identifier = str.split("=", 1)
            locationCodes.append(identifier[1])
        else:
            locationCodes.append(str)

    identifiers = s.join(locationCodes)

    return identifiers


def parse_iso_codes(jsn):
    iso_codes = dict()
    s = "_"

    for attr in jsn["spatialCoverage"]:
        try:
             if not attr["relatedIdentifiers"]:
                 iso_codes["ISO_3166"] = "null"
                 iso_codes["ISO_3166-1"] = "null"
                 iso_codes["ISO_3166-1_alpha-3"] = "null"
             else:
                 iso_lst = []

                 for sub_attr in attr["relatedIdentifiers"]:
                     iso_lst.append(sub_attr["identifierSource"])

                     code_label = sub_attr["identifierSource"]
                     splt = code_label.split(" ")
                     key = s.join(splt)

                     iso_codes[key] = sub_attr["identifier"]

                 if "ISO 3166" not in iso_lst:
                     iso_codes["ISO_3166"] = "null"
                 if "ISO 3166-1" not in iso_lst:
                     iso_codes["ISO_3166-1"] = "null"
                 if "ISO 3166-1 alpha-3" not in iso_lst:
                     iso_codes["ISO_3166-1_alpha-3"] = "null"
        except:
            try:
                if not attr["alternateIdentifiers"]:
                    iso_codes["ISO_3166"] = "null"
                    iso_codes["ISO_3166-1"] = "null"
                    iso_codes["ISO_3166-1_alpha-3"] = "null"
                else:
                    iso_lst = []

                    for sub_attr in attr["alternateIdentifiers"]:
                        iso_lst.append(sub_attr["identifierSource"])

                        code_label = sub_attr["identifierSource"]
                        splt = code_label.split(" ")
                        key = s.join(splt)

                        iso_codes[key] = sub_attr["identifier"]

                    if "ISO 3166" not in iso_lst:
                        iso_codes["ISO_3166"] = "null"
                    if "ISO 3166-1" not in iso_lst:
                        iso_codes["ISO_3166-1"] = "null"
                    if "ISO 3166-1 alpha-3" not in iso_lst:
                        iso_codes["ISO_3166-1_alpha-3"] = "null"
            except:
                iso_codes["ISO_3166"] = "null"
                iso_codes["ISO_3166-1"] = "null"
                iso_codes["ISO_3166-1_alpha-3"] = "null"


    return iso_codes


def parse_nested_attr(jsn, attribute_1, attribute_2):
    if not jsn[attribute_1][attribute_2]:
        nested_attr = "null"
    else:
        nested_attr = jsn[attribute_1][attribute_2]

    return nested_attr


# For Project Tycho JSON, specifically
def parse_disease_name(jsn):
    for attr in jsn["isAbout"]:
        if "SNOMED" in attr["identifier"]["identifier"]:
            disease_name = attr["name"]
        else:
            disease_name = "null"

        return disease_name


def parse_json(fhand):
    dataset_info = dict()

    dataset_info["title"] = fhand["title"]
    dataset_info["datasetIdentifier"] = parse_dataset_id(fhand)
    dataset_info["authors"] = parse_authors(fhand)
    dataset_info["created"] = parse_dates(fhand).get("creationDate")
    dataset_info["modified"] = parse_dates(fhand).get("modificationDate")
    dataset_info["curated"] = parse_dates(fhand).get("curationDate")
    dataset_info["accessed"] = parse_dates(fhand).get("accessedDate")
    dataset_info["landingPage"] = parse_landing_page(fhand)
    dataset_info["accessPage"] = parse_access_page(fhand)
    dataset_info["format"] = parse_format(fhand)
    dataset_info["conformsTo"] = parse_standard(fhand)
    dataset_info["geography"] = parse_geo(fhand)
    dataset_info["apolloLocationCode"] = parse_geo_id(fhand)
    dataset_info["ISO_3166"] = parse_iso_codes(fhand).get("ISO_3166")
    dataset_info["ISO_3166-1"] = parse_iso_codes(fhand).get("ISO_3166-1")
    dataset_info["ISO_3166-1_alpha-3"] = parse_iso_codes(fhand).get("ISO_3166-1_alpha-3")
    dataset_info["disease"] = parse_disease_name(fhand)

    #dataset_info["identifier"] = parse_nested_attr(fhand, "identifier", "identifier")
    #dataset_info["identifier_source"] = parse_nested_attr(fhand, "identifier", "identifierSource")
    #dataset_info["name"] = fhand["name"]
    #dataset_info["type"] = parse_nested_attr(fhand, "type", "value")
    #dataset_info["type_IRI"] = parse_nested_attr(fhand, "type", "valueIRI")
    #dataset_info["description"] = fhand["description"]
    #dataset_info["licenses"] = fhand["licenses"][0]["name"]
    #dataset_info["version"] = fhand["version"]

    return dataset_info


if __name__ == '__main__':
    dhand = input("Please enter name of directory with JSON files: ")
    output_fname = input("Please enter the desired name for the output file: ") + ".txt"

    dsets_dicts = []

    for filename in os.listdir(dhand):
        filename = dhand + "/" + filename

        with open(filename) as jsn_data:
            hand = json.load(jsn_data)

            dsets_dicts.append(parse_json(hand))

            jsn_data.close()


    with open(output_fname, "a") as dats_f:
        fieldnames = \
            ['title', 'datasetIdentifier', 'disease', 'authors', 'created', 'modified', 'curated', 'accessed',
             'landingPage', 'accessPage', 'format', 'conformsTo', 'geography', 'apolloLocationCode', 'ISO_3166',
             'ISO_3166-1', 'ISO_3166-1_alpha-3']

        #fieldnames = ['name', 'identifier', 'identifier_source', 'type', 'type_IRI', 'description', 'licenses', 'version']

        dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
        dict_writer.writeheader()

        for dset in dsets_dicts:
            dict_writer.writerow(dset)