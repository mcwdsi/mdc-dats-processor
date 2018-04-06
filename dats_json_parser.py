import os
import json
from csv import DictWriter
import datetime as dt
import urllib.request
import urllib.parse
import time


def call_api(url, header, identifier=False):
    if identifier:
        url = url + identifier
    r = urllib.request.Request(url, headers=header)
    rhand = urllib.request.urlopen(r)
    convert_to_string = rhand.read().decode('latin-1')
    data = json.loads(convert_to_string)
    #time.sleep(1)

    return data


def parse_authors(jsn):
    author_list = []
    s = ", "

    try:
        if not jsn["creators"]:
            author_list.append("null")
        else:
            for i in jsn["creators"]:
                last = i["lastName"]
                first = i["firstName"]

                str = first + " " + last
                author_list.append(str)

        authors = s.join(author_list)

        return authors

    except KeyError:
        if not jsn["creators"]:
            author_list.append("null")
        elif not jsn["creators"][0]["name"]:
            author_list = "null"
        else:
            author_list = jsn["creators"][0]["name"]["description"]


        return author_list


def parse_dates(jsn):
    dates = dict()

    try:
        for element in jsn["distributions"]:
            if not element["dates"]:
                dates["creationDate"] = "null"
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
                    if "accessed" not in date_lst:
                        dates["accessedDate"] = "null"

                    continue
    except:
        dates["creationDate"] = "null"
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
    try:
        if jsn["identifier"]["identifier"] == "":
            id = "null"
        else:
            id = jsn["identifier"]["identifier"]
    except:
        id = "null"

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

        if locationCodes:
            if "http" in str:
                print(locationCodes)
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
    if not jsn.get(attribute_1):
        nested_attr = "null"
    elif not jsn[attribute_1][attribute_2]:
        nested_attr = "null"
    else:
        nested_attr = jsn[attribute_1][attribute_2]

    return nested_attr


# For Project Tycho JSON, specifically
def parse_disease_name(jsn):
    try:
        for attr in jsn["isAbout"]:
            if attr["identifier"]["identifierSource"] == "https://biosharing.org/bsg-s000098":
                disease_name = attr["name"]
            else:
                disease_name = "null"

            return disease_name
    except KeyError:
        disease_name = "null"

        return disease_name


def parse_description(jsn):
    description = jsn['description']
    cleaned_description = description.replace('\n', ', ')

    return cleaned_description


def parse_licenses(jsn):
    try:
        for license in jsn["licenses"]:
            if not license["name"]:
                license_name = "null"
            else:
                license_name = license["name"]

            return license_name
    except KeyError:
        license_name = "null"

        return license_name


def parse_version(jsn):
    if not jsn["version"]:
        license = "null"
    else:
        license = jsn["version"]

    return license


def parse_extra(jsn):
    extra_properties = dict()
    categories = []

    for property in jsn["extraProperties"]:
        categories.append(property["category"])

        if "human" in property["category"]:
            if not property["values"][0]["value"]:
                extra_properties["human_value"] = "null"
            else:
                extra_properties["human_value"] = property["values"][0]["value"]

            if not property["values"][0]["valueIRI"]:
                extra_properties["human_value_IRI"] = "null"
            else:
                extra_properties["human_value_IRI"] = property["values"][0]["valueIRI"]


        if "machine" in property["category"]:
            if not property["values"][0]["value"]:
                extra_properties["machine_value"] = "null"
            else:
                extra_properties["machine_value"] = property["values"][0]["value"]

            if not property["values"][0]["valueIRI"]:
                extra_properties["machine_value_IRI"] = "null"
            else:
                extra_properties["machine_value_IRI"] = property["values"][0]["valueIRI"]


    if "human-readable specification of data format" not in categories:
        extra_properties["human_value"] = "null"
        extra_properties["human_value_IRI"] = "null"


    if "machine-readable specification of data format" not in categories:
        extra_properties["machine_value"] = "null"
        extra_properties["machine_value_IRI"] = "null"


    return extra_properties


def parse_json(fhand):
    dataset_info = dict()

    try:
        dataset_info["title"] = fhand["title"]
        dataset_info["description"] = fhand["description"]
        dataset_info["datasetIdentifier"] = parse_dataset_id(fhand)
        dataset_info["authors"] = parse_authors(fhand)
        dataset_info["created"] = parse_dates(fhand).get("creationDate")
        dataset_info["modified"] = parse_dates(fhand).get("modificationDate")
        dataset_info["accessed"] = parse_dates(fhand).get("accessedDate")
        dataset_info["landingPage"] = parse_landing_page(fhand)
        dataset_info["accessPage"] = parse_access_page(fhand)
        dataset_info["format"] = parse_format(fhand)
        dataset_info["conformsTo"] = parse_standard(fhand)
        dataset_info["license"] = parse_licenses(fhand)
        dataset_info["geography"] = parse_geo(fhand)
        dataset_info["apolloLocationCode"] = parse_geo_id(fhand)
        dataset_info["ISO_3166"] = parse_iso_codes(fhand).get("ISO_3166")
        dataset_info["ISO_3166-1"] = parse_iso_codes(fhand).get("ISO_3166-1")
        dataset_info["ISO_3166-1_alpha-3"] = parse_iso_codes(fhand).get("ISO_3166-1_alpha-3")
        dataset_info["disease"] = parse_disease_name(fhand)
    except:
        dataset_info["identifier"] = parse_nested_attr(fhand, "identifier", "identifier")
        dataset_info["identifier_source"] = parse_nested_attr(fhand, "identifier", "identifierSource")
        dataset_info["name"] = fhand["name"]
        dataset_info["type"] = parse_nested_attr(fhand, "type", "value")
        dataset_info["type_IRI"] = parse_nested_attr(fhand, "type", "valueIRI")
        dataset_info["description"] = fhand["description"]
        dataset_info["licenses"] = parse_licenses(fhand)
        dataset_info["version"] = parse_version(fhand)
        dataset_info["human-readable_data_format_specification_value"] = parse_extra(fhand).get("human_value")
        dataset_info["human-readable_data_format_specification_value_IRI"] = parse_extra(fhand).get("human_value_IRI")
        dataset_info["machine-readable_data_format_specification_value"] = parse_extra(fhand).get("machine_value")
        dataset_info["machine-readable_data_format_specification_value_IRI"] = parse_extra(fhand).get("machine_value_IRI")

    return dataset_info


def parse_data_standard(data):
    data_info = dict()

    data_info["identifier"] = parse_nested_attr(data, "identifier", "identifier")
    data_info["identifier_source"] = parse_nested_attr(data, "identifier", "identifierSource")
    data_info["name"] = data["name"]
    data_info["type"] = parse_nested_attr(data, "type", "value")
    data_info["type_IRI"] = parse_nested_attr(data, "type", "valueIRI")
    data_info["description"] = parse_description(data)
    data_info["licenses"] = parse_licenses(data)
    data_info["version"] = parse_version(data)
    data_info["human-readable_data_format_specification_value"] = parse_extra(data).get("human_value")
    data_info["human-readable_data_format_specification_value_IRI"] = parse_extra(data).get("human_value_IRI")
    data_info["machine-readable_data_format_specification_value"] = parse_extra(data).get("machine_value")
    data_info["machine-readable_data_format_specification_value_IRI"] = parse_extra(data).get("machine_value_IRI")

    return data_info


def parse_datasets(data):
    dataset_info = dict()

    dataset_info["title"] = data["title"]
    dataset_info["description"] = data["description"]
    dataset_info["datasetIdentifier"] = parse_dataset_id(data)
    dataset_info["authors"] = parse_authors(data)
    dataset_info["created"] = parse_dates(data).get("creationDate")
    dataset_info["modified"] = parse_dates(data).get("modificationDate")
    dataset_info["accessed"] = parse_dates(data).get("accessedDate")
    dataset_info["landingPage"] = parse_landing_page(data)
    dataset_info["accessPage"] = parse_access_page(data)
    dataset_info["format"] = parse_format(data)
    dataset_info["conformsTo"] = parse_standard(data)
    dataset_info["license"] = parse_licenses(data)
    dataset_info["geography"] = parse_geo(data)
    dataset_info["apolloLocationCode"] = parse_geo_id(data)
    dataset_info["ISO_3166"] = parse_iso_codes(data).get("ISO_3166")
    dataset_info["ISO_3166-1"] = parse_iso_codes(data).get("ISO_3166-1")
    dataset_info["ISO_3166-1_alpha-3"] = parse_iso_codes(data).get("ISO_3166-1_alpha-3")
    dataset_info["disease"] = parse_disease_name(data)

    return dataset_info


def check_type(jsn, attribute, index=0):
    if not jsn.get('types'):
        info_type = "null"
    elif not len(jsn['types']) > index:
        info_type = "null"
    elif not jsn['types']:
        info_type = "null"
    elif not jsn['types'][index][attribute]:
        info_type = "null"
    elif not jsn['types'][index][attribute]['value']:
        info_type = "null"
    else:
        info_type = jsn['types'][index][attribute]['value']

    return info_type


def check_is_about(jsn):
    if not jsn.get('isAbout'):
        is_about = "null"
    elif not jsn['isAbout']:
        is_about = "null"
    elif not jsn['isAbout'][0]['name']:
        is_about = "null"
    else:
        is_about = jsn['isAbout'][0]['name']

    return is_about


def check_id(jsn):
    if not jsn.get('identifier'):
        identifier = "null"
    elif not jsn['identifier']:
        identifier = "null"
    elif not jsn['identifier']['identifier']:
        identifier = "null"
    else:
        identifier = jsn['identifier']['identifier']

    return identifier


def parse_climate_dataset(data):
    dataset_info = dict()

    dataset_info["title"] = data["title"]
    dataset_info["description"] = data["description"]
    dataset_info["authors"] = parse_authors(data)
    dataset_info["landingPage"] = parse_landing_page(data)
    dataset_info["accessPage"] = parse_access_page(data)
    dataset_info["format"] = parse_format(data)
    dataset_info["license"] = parse_licenses(data)
    dataset_info["geography"] = parse_geo(data)
    dataset_info["apolloLocationCode"] = parse_geo_id(data)
    dataset_info["ISO_3166"] = parse_iso_codes(data).get("ISO_3166")
    dataset_info["ISO_3166-1"] = parse_iso_codes(data).get("ISO_3166-1")
    dataset_info["ISO_3166-1_alpha-3"] = parse_iso_codes(data).get("ISO_3166-1_alpha-3")

    return dataset_info


def write_to_file(fname, list_of_dictionaries, content_type):
    with open(fname, "a") as dats_f:
        if content_type == "data-format":
            fieldnames = ['name', 'identifier', 'identifier_source', 'type', 'type_IRI', 'description', 'licenses',
                          'version', 'human-readable_data_format_specification_value',
                          'human-readable_data_format_specification_value_IRI',
                          'machine-readable_data_format_specification_value',
                          'machine-readable_data_format_specification_value_IRI']

            dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
            dict_writer.writeheader()

            for dstandard in list_of_dictionaries:
                dict_writer.writerow(dstandard)

        if content_type == "dataset":
            fieldnames = ['title', 'description', 'datasetIdentifier', 'disease', 'authors', 'created', 'modified', 'accessed',
                     'landingPage', 'accessPage', 'format', 'conformsTo', 'license', 'geography', 'apolloLocationCode', 'ISO_3166',
                     'ISO_3166-1', 'ISO_3166-1_alpha-3']

            dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
            dict_writer.writeheader()

            for dset in list_of_dictionaries:
                dict_writer.writerow(dset)


if __name__ == '__main__':
    access_hand = input("Please indicate whether you will be calling the MDC API or parsing a local JSON file: [api]/[local]: ")

    today = dt.datetime.today().strftime("%Y-%m-%d_T%H-%M")

    header = { 'Accept': 'application/json' }
    metadata_type_base_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/metadata-type?identifier="
    metadata_base_url = "http://betaweb.rods.pitt.edu/digital-commons-dev/api/v1/identifiers/metadata?identifier="
    category_type_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/category?identifier="

    '''
    Code for accessing MDC DATS JSON by calling the API
    '''

    if access_hand == "api":
        api_url = input("Please enter URL of API: ")
        content_type = input("Please indicate which content type you'd like: [data-format]/[dataset]: ")

        get_global_identifiers = call_api(api_url, header)

        '''
        Code for processing data formats JSON DATS
        '''

        if content_type == 'data-format':
            dstandard_dicts = []
            output_fname = "data-formats-dats-info-" + today + ".txt"

            try:
                for identifier in get_global_identifiers:
                    identifier = urllib.parse.quote(identifier, safe='')
                    get_formats = call_api(metadata_type_base_url, header, identifier=identifier)

                    if get_formats['datatype'] == 'DataStandard':
                        get_format_metadata = call_api(metadata_base_url, header, identifier=identifier)
                        dstandard_dicts.append(parse_data_standard(get_format_metadata))

            except ConnectionResetError:
                print(identifier)

            write_to_file(output_fname, dstandard_dicts, content_type)
            print('Data formats: ', len(dstandard_dicts))

        '''
        Code for processing datasets JSON DATS
        '''

        if content_type == 'dataset':
            tycho_dset_dicts = []
            climate_dset_dicts = []
            spew_dset_dicts = []
            synthia_dset_dicts = []
            case_series_dset_dicts = []
            chikv_epidemic_dset_dicts = []
            ebov_epidemic_dset_dicts = []
            zikv_epidemic_dset_dicts = []
            ids_dset_dicts = []
            mortality_dset_dicts = []
            disease_surveillance_dset_dicts = []
            web_dset_dicts = []

            tycho_output_fname = "tycho-dats-info-" + today + ".txt"
            spew_output_fname = "spew-dats-info-" + today + ".txt"
            synthia_output_fname = "synthia-dats-info-" + today + ".txt"
            climate_output_fname = "climate-dats-info-" + today + ".txt"
            case_series_output_fname = "case-series-dats-info-" + today + ".txt"
            chikv_output_fname = "chikv-dats-info-" + today + ".txt"
            ebov_output_fname = "ebola-dats-info-" + today + ".txt"
            zikv_output_fname = "zika-dats-info-" + today + ".txt"
            ids_output_fname = "infectious-disease-dats-info-" + today + ".txt"
            mortality_out_fname = "mortality-dats-info-" + today + ".txt"
            disease_surveillance_output_fname = "disease-surveillance-dats-info-" + today + ".txt"
            web_dset_output_fname = "websites-with-data-dats-info-" + today + ".txt"

            datasets_witout_ids = []

            print("Getting datasets...")

            # Remove identifiers for non-datasets and sort datasets by category
            for id in get_global_identifiers:
                if id == "identifier will be created as time of release" : continue

                id = urllib.parse.quote(id, safe='')
                get_datasets = call_api(metadata_type_base_url, header, identifier=id)

                try:
                    if get_datasets['datatype'] == 'Dataset':
                        get_dataset_category = call_api(category_type_url, header, identifier=id)

                        try:
                            if get_dataset_category[2] == 'Disease surveillance data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)

                                if len(get_dataset_category) == 6 and get_dataset_category[5] == '[Project Tycho Datasets]':
                                    tycho_dset_dicts.append(parse_datasets(get_metadata))
                                else:
                                    disease_surveillance_dset_dicts.append(parse_datasets(get_metadata))

                            if get_dataset_category[2] == 'Case series data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                case_series_dset_dicts.append(parse_datasets(get_metadata))

                            if get_dataset_category[2] == 'Weather and climate data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                climate_dset_dicts.append(parse_datasets(get_metadata))

                            if get_dataset_category[2] == 'Epidemic data':
                                try:
                                    if get_dataset_category[3] == 'Ebola epidemics':
                                        get_metadata = call_api(metadata_base_url, header, identifier=id)
                                        ebov_epidemic_dset_dicts.append(parse_datasets(get_metadata))
                                except IndexError : continue

                            if get_dataset_category[2] == 'Infectious disease scenario data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                ids_dset_dicts.append(parse_datasets(get_metadata))

                            if get_dataset_category[2] == 'Mortality data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                mortality_dset_dicts.append(parse_datasets(get_metadata))

                            try:
                                if get_dataset_category[3] == 'Synthia? datasets':
                                    get_metadata = call_api(metadata_base_url, header, identifier=id)
                                    synthia_dset_dicts.append(parse_datasets(get_metadata))
                            except IndexError : continue

                            try:
                                if get_dataset_category[3] == 'SPEW datasets':
                                    get_metadata = call_api(metadata_base_url, header, identifier=id)
                                    spew_dset_dicts.append(parse_datasets(get_metadata))
                            except IndexError : continue

                            if get_dataset_category[2] == 'Websites with data':
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                web_dset_dicts.append(parse_datasets(get_metadata))

                        except KeyError:
                            print("Error")

                    else : continue

                except ConnectionResetError:
                    print(id)

            '''

            for element in data:
                if 'Dataset' in element['type']:
                    title = element['content']['title']

                    if 'epidemic' in check_type(element['content'], 'information') and 'Chikungunya' in check_is_about(element['content']):
                        if check_id(element['content']) == "null":
                            datasets_witout_ids.append(title)
                        chikv_epidemic_dset_dicts.append(parse_datasets(element['content']))

                    if 'epidemic' in check_type(element['content'], 'information') and 'zika' in check_is_about(element['content']).lower():
                        zikv_epidemic_dset_dicts.append(parse_datasets(element['content']))
            '''
            write_to_file(tycho_output_fname, tycho_dset_dicts, content_type)
            write_to_file(spew_output_fname, spew_dset_dicts, content_type)
            write_to_file(synthia_output_fname, synthia_dset_dicts, content_type)
            write_to_file(climate_output_fname, climate_dset_dicts, content_type)
            write_to_file(case_series_output_fname, case_series_dset_dicts, content_type)
            #write_to_file(chikv_output_fname, chikv_epidemic_dset_dicts, content_type)
            write_to_file(ebov_output_fname, ebov_epidemic_dset_dicts, content_type)
            #write_to_file(zikv_output_fname, zikv_epidemic_dset_dicts, content_type)
            write_to_file(ids_output_fname, ids_dset_dicts, content_type)
            write_to_file(mortality_out_fname, mortality_dset_dicts, content_type)
            write_to_file(disease_surveillance_output_fname, disease_surveillance_dset_dicts, content_type)
            write_to_file(web_dset_output_fname, web_dset_dicts, content_type)

            print("<-------------------- Number of resources parsed for each dataset category -------------------->")
            print("\t", "Tycho: ", len(tycho_dset_dicts))
            print("\t", "SPEW: ", len(spew_dset_dicts))
            print("\t", "Synthia: ", len(synthia_dset_dicts))
            print("\t", "Climate: ", len(climate_dset_dicts))
            print("\t", "Case series: ", len(case_series_dset_dicts))
            print("\t", "CHIKV: ", len(chikv_epidemic_dset_dicts))
            print("\t", "Ebola: ", len(ebov_epidemic_dset_dicts))
            print("\t", "Zika: ", len(zikv_epidemic_dset_dicts))
            print("\t", "Infectious disease scenario: ", len(ids_dset_dicts))
            print("\t", "Mortality: ", len(mortality_dset_dicts))
            print("\t", "Surveillance: ", len(disease_surveillance_dset_dicts))
            print("\t", "Web: ", len(web_dset_dicts))

    '''
    Code for accessing MDC DATS JSON by opening local JSON file(s)
    '''

    if access_hand == "local":
        dhand = input("Please enter name of directory with JSON files: ")
        output_fname = dhand.replace("json", "info_")

        output_fname += today
        output_fname += ".txt"

        dsets_dicts = []

        for filename in os.listdir(dhand):
            filename = dhand + "/" + filename

            with open(filename) as jsn_data:
                hand = json.load(jsn_data)

                dsets_dicts.append(parse_json(hand))

                jsn_data.close()


        try:
            for dset_dict in dsets_dicts:
                x = dset_dict["title"]

            with open(output_fname, "a") as dats_f:
                fieldnames = \
                    ['title', 'description', 'datasetIdentifier', 'disease', 'authors', 'created', 'modified', 'accessed',
                     'landingPage', 'accessPage', 'format', 'conformsTo', 'license', 'geography', 'apolloLocationCode', 'ISO_3166',
                     'ISO_3166-1', 'ISO_3166-1_alpha-3']

                dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
                dict_writer.writeheader()

                for dset in dsets_dicts:
                    dict_writer.writerow(dset)
        except:
            for dset_dict in dsets_dicts:
                x = dset_dict["name"]

            with open(output_fname, "a") as dats_f:

                fieldnames = ['name', 'identifier', 'identifier_source', 'type', 'type_IRI', 'description', 'licenses',
                              'version', 'human-readable_data_format_specification_value',
                              'human-readable_data_format_specification_value_IRI',
                              'machine-readable_data_format_specification_value',
                              'machine-readable_data_format_specification_value_IRI']

                dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
                dict_writer.writeheader()

                for dset in dsets_dicts:
                    dict_writer.writerow(dset)