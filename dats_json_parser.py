import os
import json
from csv import DictWriter
import datetime as dt
import urllib.request
import urllib.parse
import time


def call_api(url, header, identifier=False):
    """Submits a request to one of the MDC API calls and returns a JSON object that contains the relevant metadata."""

    if identifier:
        url = url + identifier
    r = urllib.request.Request(url, headers=header)
    rhand = urllib.request.urlopen(r)
    convert_to_string = rhand.read().decode("latin-1")
    data = json.loads(convert_to_string)
    #time.sleep(1)
    return data


def parse_authors(jsn):
    """Parses authors' first and last names or an organization's name from the DATS and returns them as a string."""

    author_list = list()
    s = "; "

    try:
        if not jsn["creators"]:
            author_list.append("null")
        else:
            for i in jsn["creators"]:
                if i["lastName"] == "" and i["firstName"] == "":
                    return "null"
                else:
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
            author_list = jsn["creators"][0]["name"]
        return author_list


def parse_dates(jsn):
    """Parses the creation, modification, and access dates from the DATS and stores each in a Python dictionary
    and returns each as a string.
    """

    dates = dict()

    try:
        for element in jsn["distributions"]:
            if not element["dates"]:
                dates["creation_date"] = "null"
                dates["modification_date"] = "null"
                dates["accessed_date"] = "null"
            else:
                date_lst = list()
                for i in element["dates"]:
                    value = "{}_date".format(i["type"]["value"])
                    date_lst.append(value)

                    if i["date"] == "":
                        dates[value] = "null"
                    else:
                        dates[value] = i["date"]

                if "creation_date" not in date_lst:
                    dates["creation_date"] = "null"
                if "modification_date" not in date_lst:
                    dates["modification_date"] = "null"
                if "accessed_date" not in date_lst:
                    dates["accessed_date"] = "null"
                continue
    except Exception:
        dates["creation_date"] = "null"
        dates["modification_date"] = "null"
        dates["accessed_date"] = "null"
    return dates


def parse_format(jsn):
    """Parses the contents of the 'formats' JSON array in the DATS and returns them as a string."""

    try:
        s = "; "

        formats = s.join(jsn["distributions"][0]["formats"])
    except Exception:
        formats = "null"
    return formats


def parse_standard(jsn):
    """Parses the name and identifier of the data standard in the DATS and returns each of them as a string."""

    try:
        standard_name = jsn["distributions"][0]["conformsTo"][0]["name"]
        standard_identifier = jsn["distributions"][0]["conformsTo"][0]["identifier"]["identifier"]
        standard = standard_name + "; " + standard_identifier
    except Exception:
        standard = "null"
    return standard


def parse_landing_page(jsn):
    """Parses the URL of the landing page in the DATS and returns it as a string."""

    try:
        url = jsn["distributions"][0]["access"]["landingPage"]
    except Exception:
        url = "null"
    return url


def parse_access_page(jsn):
    """Parses the URL of the access page in the DATS and returns it as a string."""

    try:
        url = jsn["distributions"][0]["access"]["accessURL"]
    except Exception:
        url = "null"
    return url


def parse_dataset_id(jsn):
    """Parses the dataset identifier in the DATS and returns it as a string."""

    try:
        if jsn["identifier"]["identifier"] == "":
            id = "null"
        else:
            id = jsn["identifier"]["identifier"]
    except Exception:
        id = "null"
    return id


def parse_geo(jsn):
    """Parses the location name in the DATS and returns it as a string."""

    regions = list()
    s = "; "

    try:
        for attr in jsn["spatialCoverage"]:
            regions.append(attr["name"])
            continue

        names = s.join(regions)
        return names
    except KeyError:
        return "null"


def parse_geo_id(jsn):
    """Parses the location name in the DATS and returns it as a string."""

    locationCodes = list()
    s = "; "

    try:
        spatialCoverage = jsn["spatialCoverage"]

        for attr in spatialCoverage:
            try:
                str = attr["identifier"]["identifier"]

                if locationCodes:
                    if "http" in str:
                        print(locationCodes)
                        identifier = str.split("=", 1)
                        locationCodes.append(identifier[1])
                    else:
                        locationCodes.append(str)
                else:
                    locationCodes.append(str)
            except KeyError:
                return "null"
    except KeyError:
        return "null"

    identifiers = s.join(locationCodes)
    return identifiers


def parse_iso_codes(jsn):
    """Parses ISO 3166, ISO 3166-1, and ISO 3166-1 alpha-3 codes in the DATS and returns it as a string."""

    iso_codes = dict()
    iso3166_lst = list()
    iso3166_1_lst = list()
    iso3166_1_alpha3_lst = list()

    s = "; "

    try:
        for attr in jsn["spatialCoverage"]:
            try:
                 if not attr["relatedIdentifiers"]:
                     iso3166_lst.append("null")
                     iso3166_1_lst.append("null")
                     iso3166_1_alpha3_lst.append("null")
                 else:
                     iso_lst = list()

                     for sub_attr in attr["relatedIdentifiers"]:
                         if sub_attr["identifierSource"] == "ISO 3166":
                             iso3166_lst.append(sub_attr["identifier"])
                             iso_lst.append(sub_attr["identifierSource"])
                         elif sub_attr["identifierSource"] == "ISO 3166-1 numeric":
                             iso3166_1_lst.append(sub_attr["identifier"])
                             iso_lst.append(sub_attr["identifierSource"])
                         elif sub_attr["identifierSource"] == "ISO 3166-1 alpha-3":
                             iso3166_1_alpha3_lst.append(sub_attr["identifier"])
                             iso_lst.append(sub_attr["identifierSource"])

                     if "ISO 3166" not in iso_lst:
                         print("iso list:", iso_lst)
                         iso3166_lst.append("null")
                     if "ISO 3166-1 numeric" not in iso_lst:
                         iso3166_1_lst.append("null")
                     if "ISO 3166-1 alpha-3" not in iso_lst:
                         iso3166_1_alpha3_lst.append("null")
            except Exception:
                try:
                    if not attr["alternateIdentifiers"]:
                        iso3166_lst.append("null")
                        iso3166_1_lst.append("null")
                        iso3166_1_alpha3_lst.append("null")
                    else:
                        iso_lst = list()

                        for sub_attr in attr["alternateIdentifiers"]:
                            if sub_attr["identifierSource"] == "ISO 3166":
                                iso3166_lst.append(sub_attr["identifier"])
                                iso_lst.append(sub_attr["identifierSource"])
                            elif sub_attr["identifierSource"] == "ISO 3166-1 numeric":
                                iso3166_1_lst.append(sub_attr["identifier"])
                                iso_lst.append(sub_attr["identifierSource"])
                            elif sub_attr["identifierSource"] == "ISO 3166-1 alpha-3":
                                iso3166_1_alpha3_lst.append(sub_attr["identifier"])
                                iso_lst.append(sub_attr["identifierSource"])

                        if "ISO 3166" not in iso_lst:
                            iso3166_lst.append("null")
                        if "ISO 3166-1 numeric" not in iso_lst:
                            iso3166_1_lst.append("null")
                        if "ISO 3166-1 alpha-3" not in iso_lst:
                            iso3166_1_alpha3_lst.append("null")

                except Exception:
                    iso3166_lst.append("null")
                    iso3166_1_lst.append("null")
                    iso3166_1_alpha3_lst.append("null")

    except KeyError:
        iso3166_lst.append("null")
        iso3166_1_lst.append("null")
        iso3166_1_alpha3_lst.append("null")

    iso_codes["ISO_3166"] = s.join(iso3166_lst)
    iso_codes["ISO_3166_1"] = s.join(iso3166_1_lst)
    iso_codes["ISO_3166_1_alpha_3"] = s.join(iso3166_1_alpha3_lst)
    return iso_codes


def parse_nested_attr(jsn, attribute_1, attribute_2):
    """Parses an attribute value that is nested within another attribute value in the DATS and returns it as a
    string.
    """

    try:
        if not jsn.get(attribute_1):
            nested_attr = "null"
        elif not jsn[attribute_1][attribute_2]:
            nested_attr = "null"
        else:
            nested_attr = jsn[attribute_1][attribute_2]
        return nested_attr
    except KeyError:
        return "null"


def parse_disease_name(jsn):
    """For Project Tycho JSON, specifically.

    Parses disease names from the content of the 'isAbout' JSON array in the DATS and returns them as a string.
    """

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
    """Parses the description from the DATS and returns it as a string."""

    description = jsn["description"]
    cleaned_description = description.replace("\n", " ")
    return cleaned_description


def parse_licenses(jsn):
    """Parses the license name from the DATS and returns it as a string."""

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
    """Parses the data standard version from the DATS and returns it as a string."""

    if not jsn["version"]:
        license = "null"
    else:
        license = jsn["version"]
    return license


def parse_extra(jsn):
    """Parses the human- and machine-readable specifications and the validator for the data standard from the DATS and
    returns them as separate strings.
    """

    extra_properties = dict()
    categories = list()

    try:
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

            if "validator" in property["category"]:
                if not property["values"][0]["value"]:
                    extra_properties["validator_value"] = "null"
                else:
                    extra_properties["validator_value"] = property["values"][0]["value"]

                if not property["values"][0]["valueIRI"]:
                    extra_properties["validator_value_IRI"] = "null"
                else:
                    extra_properties["validator_value_IRI"] = property["values"][0]["valueIRI"]

        if "human-readable specification of data format" not in categories:
            extra_properties["human_value"] = "null"
            extra_properties["human_value_IRI"] = "null"

        if "machine-readable specification of data format" not in categories:
            extra_properties["machine_value"] = "null"
            extra_properties["machine_value_IRI"] = "null"

        if "validator" not in categories:
            extra_properties["validator_value"] = "null"
            extra_properties["validator_value_IRI"] = "null"
        return extra_properties
    except KeyError:
        extra_properties["human_value"] = "null"
        extra_properties["human_value_IRI"] = "null"
        extra_properties["machine_value"] = "null"
        extra_properties["machine_value_IRI"] = "null"
        extra_properties["validator_value"] = "null"
        extra_properties["validator_value_IRI"] = "null"
        return extra_properties


def parse_stored_in(jsn):
    """Parses the contents of the 'storedIn' JSON attribute in the DATS to check if the Apollo Library or the MDC are
    listed as repositories. Returns 'TRUE' or 'FALSE' for each accordingly.
    """

    try:
        stored_in = jsn["distributions"][0]["storedIn"]["name"]

        if stored_in == "Apollo Library":
            return stored_in
        elif stored_in == "MIDAS Digital Commons":
            return stored_in
    except Exception:
        return "null"


def check_if_apollo_enabled(s):
    """Checks if the name value for the 'storedIn' JSON attribute is 'Apollo Library'. Returns 'TRUE' or 'FALSE'
    accordingly.
    """

    if s == "null":
        return "null"
    elif s == "Apollo Library":
        return "TRUE"
    else:
        return "FALSE"


def check_if_on_olympus(s):
    """Checks if the name value for the 'storedIn' JSON attribute is 'MIDAS Digital Commons'. Returns 'TRUE' or 'FALSE'
    accordingly.
    """

    if s == "null":
        return "null"
    elif s == "MIDAS Digital Commons":
        return "TRUE"
    else:
        return "FALSE"


def parse_data_standard(data):
    """Extracts each metadata item from the DATS if the digital object is a data standard."""

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
    data_info["validator_value"] = parse_extra(data).get("validator_value")
    data_info["validator_value_IRI"] = parse_extra(data).get("validator_value_IRI")
    return data_info


def parse_datasets(data):
    """Extracts each metadata item from the DATS if the digital object is a dataset."""

    dataset_info = dict()

    dataset_info["title"] = data["title"]
    dataset_info["description"] = parse_description(data)
    dataset_info["dataset_identifier"] = parse_dataset_id(data)
    dataset_info["authors"] = parse_authors(data)
    dataset_info["created"] = parse_dates(data).get("creation_date")
    dataset_info["modified"] = parse_dates(data).get("modification_date")
    dataset_info["accessed"] = parse_dates(data).get("accessed_date")
    dataset_info["landing_page"] = parse_landing_page(data)
    dataset_info["access_page"] = parse_access_page(data)
    dataset_info["format"] = parse_format(data)
    dataset_info["conforms_to"] = parse_standard(data)
    dataset_info["license"] = parse_licenses(data)
    dataset_info["geography"] = parse_geo(data)
    dataset_info["apollo_location_code"] = parse_geo_id(data)
    dataset_info["iso_3166"] = parse_iso_codes(data).get("ISO_3166")
    dataset_info["iso_3166_1"] = parse_iso_codes(data).get("ISO_3166_1")
    dataset_info["iso_3166_1_alpha_3"] = parse_iso_codes(data).get("ISO_3166_1_alpha_3")
    dataset_info["disease"] = parse_disease_name(data)
    dataset_info["apollo_enabled"] = check_if_apollo_enabled(parse_stored_in(data))
    dataset_info["on_olympus"] = check_if_on_olympus(parse_stored_in(data))
    return dataset_info


def check_type(jsn, attribute, index=0):
    """Checks the value of each attribute in the 'types' array of each digital objects in the DATS."""

    if not jsn.get("types"):
        info_type = "null"
    elif not len(jsn["types"]) > index:
        info_type = "null"
    elif not jsn["types"]:
        info_type = "null"
    elif not jsn["types"][index][attribute]:
        info_type = "null"
    elif not jsn["types"][index][attribute]["value"]:
        info_type = "null"
    else:
        info_type = jsn["types"][index][attribute]["value"]
    return info_type


def check_is_about(jsn):
    """Checks the value of each JSON attribute in the 'isAbout' array of each digital objects in the DATS."""

    if not jsn.get("isAbout"):
        is_about = "null"
    elif not jsn["isAbout"]:
        is_about = "null"
    elif not jsn["isAbout"][0]["name"]:
        is_about = "null"
    else:
        is_about = jsn["isAbout"][0]["name"]
    return is_about


def check_id(jsn):
    """Checks the value of the 'identifier' attribute for each digital objects in the DATS."""

    if not jsn.get("identifier"):
        identifier = "null"
    elif not jsn["identifier"]:
        identifier = "null"
    elif not jsn["identifier"]["identifier"]:
        identifier = "null"
    else:
        identifier = jsn["identifier"]["identifier"]
    return identifier


def write_to_file(fname, list_of_dictionaries, content_type):
    """Writes the metadata for each digital object to a tab-delimited text file."""

    with open(fname, "a") as dats_f:
        if content_type == "data-format":
            fieldnames = ["name",
                          "identifier",
                          "identifier_source",
                          "type",
                          "type_IRI",
                          "description",
                          "licenses",
                          "version",
                          "human-readable_data_format_specification_value",
                          "human-readable_data_format_specification_value_IRI",
                          "machine-readable_data_format_specification_value",
                          "machine-readable_data_format_specification_value_IRI",
                          "validator_value",
                          "validator_value_IRI"]

            dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
            dict_writer.writeheader()

            for dstandard in list_of_dictionaries:
                dict_writer.writerow(dstandard)

        if content_type == "dataset":
            fieldnames = ["title",
                          "description",
                          "dataset_identifier",
                          "disease",
                          "authors",
                          "created",
                          "modified",
                          "accessed",
                          "landing_page",
                          "access_page",
                          "format",
                          "conforms_to",
                          "license",
                          "geography",
                          "apollo_location_code",
                          "iso_3166",
                          "iso_3166_1",
                          "iso_3166_1_alpha_3",
                          "apollo_enabled",
                          "on_olympus"]

            dict_writer = DictWriter(dats_f, fieldnames=fieldnames, delimiter="\t")
            dict_writer.writeheader()

            for dset in list_of_dictionaries:
                dict_writer.writerow(dset)


if __name__ == "__main__":
    today = dt.datetime.today().strftime("%Y-%m-%d_T%H-%M")

    header = { "Accept": "application/json" }

    #metadata_type_base_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/metadata-type?identifier="
    #metadata_base_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/metadata?identifier="
    #category_type_url = "http://betaweb.rods.pitt.edu:80/digital-commons-dev/api/v1/identifiers/category?identifier="

    #api_url = input("Please enter URL of API: ")
    content_type = input("Please indicate which content type you would like: [data-format]/[dataset]: ")

    #get_global_identifiers = call_api(api_url, header)

    """Code for processing data formats JSON DATS """

    if content_type == "data-format":
        dstandard_dicts = list()
        output_fname = "data-formats-dats-info-" + today + ".txt"

        r = urllib.request.Request("http://betaweb.rods.pitt.edu/digital-commons-dev/api/v1/contents",
                                   headers=header)
        rhand = urllib.request.urlopen(r)
        convert_to_string = rhand.read().decode("latin-1")
        data = json.loads(convert_to_string)

        for element in data:
            if element["type"] == "edu.pitt.isg.mdc.dats2_2.DataStandard":
                dstandard_dicts.append(parse_data_standard(element["content"]))

        write_to_file(output_fname, dstandard_dicts, content_type)
        print("Data formats: ", len(dstandard_dicts))


    """Code for processing datasets JSON DATS"""

    if content_type == "dataset":
        tycho_dset_dicts = list()
        spew_dset_dicts = list()
        synthia_dset_dicts = list()
        case_series_dset_dicts = list()
        chikv_epidemic_dset_dicts = list()
        ebov_epidemic_dset_dicts = list()
        zikv_epidemic_dset_dicts = list()
        ids_dset_dicts = list()
        mortality_dset_dicts = list()
        disease_surveillance_dset_dicts = list()
        web_dset_dicts = list()
        location_dset_dicts = list()

        tycho_output_fname = "tycho-dats-info-" + today + ".txt"
        spew_output_fname = "spew-dats-info-" + today + ".txt"
        synthia_output_fname = "synthia-dats-info-" + today + ".txt"
        case_series_output_fname = "case-series-dats-info-" + today + ".txt"
        chikv_output_fname = "chikv-dats-info-" + today + ".txt"
        ebov_output_fname = "ebola-dats-info-" + today + ".txt"
        zikv_output_fname = "zika-dats-info-" + today + ".txt"
        ids_output_fname = "infectious-disease-dats-info-" + today + ".txt"
        mortality_out_fname = "mortality-dats-info-" + today + ".txt"
        disease_surveillance_output_fname = "disease-surveillance-dats-info-" + today + ".txt"
        web_dset_output_fname = "websites-with-data-dats-info-" + today + ".txt"
        location_dset_output_fname = "location-dats-info-" + today + ".txt"

        datasets_witout_ids = list()

        print("Getting datasets (may take a few minutes)...")


        """Code for retrieving metadata using the get-identifiers, get-metadata-type, and get-category API calls

        This code does not include the requests for Chikungunya and Zika epidemic dataset metadata since these
        do not have unique identifiers.
        """

        """# Remove identifiers for non-datasets and sort datasets by category
        for id in get_global_identifiers:
            if id == "identifier will be created as time of release" : continue

            id = urllib.parse.quote(id, safe="")
            get_datasets = call_api(metadata_type_base_url, header, identifier=id)

            try:
                if get_datasets["datatype"] == "Dataset":
                    get_dataset_category = call_api(category_type_url, header, identifier=id)

                    if get_dataset_category[2] == "Disease surveillance data":
                        get_metadata = call_api(metadata_base_url, header, identifier=id)

                        if len(get_dataset_category) == 6:
                            if get_dataset_category[5] == "[Project Tycho Datasets]":
                                tycho_dset_dicts.append(parse_datasets(get_metadata))
                        else:
                            print(id)
                            disease_surveillance_dset_dicts.append(parse_datasets(get_metadata))

                    if get_dataset_category[2] == "Case series data":
                        get_metadata = call_api(metadata_base_url, header, identifier=id)
                        case_series_dset_dicts.append(parse_datasets(get_metadata))

                    if get_dataset_category[2] == "Epidemic data":
                        try:
                            if get_dataset_category[3] == "Ebola epidemics":
                                get_metadata = call_api(metadata_base_url, header, identifier=id)
                                ebov_epidemic_dset_dicts.append(parse_datasets(get_metadata))
                        except IndexError : continue

                    if get_dataset_category[2] == "Infectious disease scenario data":
                        get_metadata = call_api(metadata_base_url, header, identifier=id)
                        ids_dset_dicts.append(parse_datasets(get_metadata))

                    if get_dataset_category[2] == "Mortality data":
                        get_metadata = call_api(metadata_base_url, header, identifier=id)
                        mortality_dset_dicts.append(parse_datasets(get_metadata))

                    try:
                        if get_dataset_category[3] == "Synthia? datasets":
                            get_metadata = call_api(metadata_base_url, header, identifier=id)
                            synthia_dset_dicts.append(parse_datasets(get_metadata))
                    except IndexError : continue

                    try:
                        if get_dataset_category[3] == "SPEW datasets":
                            get_metadata = call_api(metadata_base_url, header, identifier=id)
                            spew_dset_dicts.append(parse_datasets(get_metadata))
                    except IndexError : continue

                    if get_dataset_category[1] == "Websites with data":
                        get_metadata = call_api(metadata_base_url, header, identifier=id)
                        web_dset_dicts.append(parse_datasets(get_metadata))

                else : continue

            except ConnectionResetError:
                print(id)
        """

        r = urllib.request.Request("http://betaweb.rods.pitt.edu/digital-commons-dev/api/v1/contents", headers=header)
        rhand = urllib.request.urlopen(r)
        convert_to_string = rhand.read().decode("latin-1")
        data = json.loads(convert_to_string)

        for element in data:
            if "Dataset" in element["type"]:
                title = element["content"]["title"]
                identifier = element["content"]["identifier"]["identifier"]

                if identifier == "https://data.cdc.gov/api/views/ei7y-3g6s":
                    disease_surveillance_dset_dicts.append(parse_datasets(element["content"]))

                if identifier == "https://data.sfgov.org/api/views/yg87-cd6v" \
                        or identifier == "https://data.kingcounty.gov/api/views/7pbe-yd3f" \
                        or identifier == "https://data.cdc.gov/api/views/cjae-szjv" \
                        or identifier == "https://data.cityofnewyork.us/api/views/w9ei-idxz" \
                        or identifier == "https://data.cityofnewyork.us/api/views/kku6-nxdu":
                    location_dset_dicts.append(parse_datasets(element["content"]))

                if identifier == "https://doi.org/10.5281/zenodo.580104":
                    ids_dset_dicts.append(parse_datasets(element["content"]))

                if identifier == "MIDAS-ISG:WS-000487":
                    mortality_dset_dicts.append(parse_datasets(element["content"]))

                if "epidemic" in check_type(element["content"], "information") and "Chikungunya" in check_is_about(element["content"]):
                    if check_id(element["content"]) == "null":
                        datasets_witout_ids.append(title)
                    chikv_epidemic_dset_dicts.append(parse_datasets(element["content"]))

                if "epidemic" in check_type(element["content"], "information") and "zika" in check_is_about(element["content"]).lower():
                    zikv_epidemic_dset_dicts.append(parse_datasets(element["content"]))

                if "epidemic" in check_type(element["content"], "information") and ("ebola" in check_is_about(element["content"]).lower() or "Sudan virus" in check_is_about(element["content"])):
                    ebov_epidemic_dset_dicts.append(parse_datasets(element["content"]))

                if "rabies" in title.lower() and "united states" in title.lower():
                    case_series_dset_dicts.append(parse_datasets(element["content"]))

                try:
                    if "tycho" in element["content"]["identifier"]["identifier"]:
                        tycho_dset_dicts.append(parse_datasets(element["content"]))
                except KeyError : continue

                if "SPEW" in element["content"]["description"]:
                    spew_dset_dicts.append(parse_datasets(element["content"]))

                try:
                    if len(element["content"]["types"]) > 2:
                        if element["content"]["types"][2]["platform"]["value"] == "SYNTHIA":
                            synthia_dset_dicts.append(parse_datasets(element["content"]))
                except KeyError : continue

                if identifier == "MIDAS-ISG:WS-000494" \
                        or identifier == "https://data.cdc.gov/browse?category=MMWR" \
                        or identifier == "MIDAS-ISG:WS-000484" \
                        or identifier == "MIDAS-ISG:WS-000486" \
                        or identifier == "http://www2.datasus.gov.br/DATASUS/index.php?area=0203" \
                        or identifier == "MIDAS-ISG:WS-000023" \
                        or identifier == "https://www.moh.gov.sg/content/moh_web/home/diseases_and_conditions.html":
                    disease_surveillance_dset_dicts.append(parse_datasets(element["content"]))

                try:
                    if element["content"]["extraProperties"][0]["category"] == "website":
                            web_dset_dicts.append(parse_datasets(element["content"]))
                    else:
                        disease_surveillance_dset_dicts.append(parse_datasets(element["content"]))
                except KeyError : continue

        print("Writing output from Project Tycho dataset DATS to file...")
        write_to_file(tycho_output_fname, tycho_dset_dicts, content_type)
        print("Writing output from SPEW dataset DATS to file...")
        write_to_file(spew_output_fname, spew_dset_dicts, content_type)
        print("Writing output from Synthia dataset DATS to file...")
        write_to_file(synthia_output_fname, synthia_dset_dicts, content_type)
        print("Writing output from Case Series dataset DATS to file...")
        write_to_file(case_series_output_fname, case_series_dset_dicts, content_type)
        print("Writing output from Chikungunya dataset DATS to file...")
        write_to_file(chikv_output_fname, chikv_epidemic_dset_dicts, content_type)
        print("Writing output from Ebola dataset DATS to file...")
        write_to_file(ebov_output_fname, ebov_epidemic_dset_dicts, content_type)
        print("Writing output from Zika dataset DATS to file...")
        write_to_file(zikv_output_fname, zikv_epidemic_dset_dicts, content_type)
        print("Writing output from Infectious Disease Scenario dataset DATS to file...")
        write_to_file(ids_output_fname, ids_dset_dicts, content_type)
        print("Writing output from Mortality dataset DATS to file...")
        write_to_file(mortality_out_fname, mortality_dset_dicts, content_type)
        print("Writing output from Disease Surveillance dataset DATS to file...")
        write_to_file(disease_surveillance_output_fname, disease_surveillance_dset_dicts, content_type)
        print("Writing output from Websites with data DATS to file...")
        write_to_file(web_dset_output_fname, web_dset_dicts, content_type)
        print("Writing output from Location dataset DATS to file...")
        write_to_file(location_dset_output_fname, location_dset_dicts, content_type)

        print("<-------------------- Number of resources parsed for each dataset category -------------------->")
        print("\t", "Tycho: ", len(tycho_dset_dicts))
        print("\t", "SPEW: ", len(spew_dset_dicts))
        print("\t", "Synthia: ", len(synthia_dset_dicts))
        print("\t", "Case series: ", len(case_series_dset_dicts))
        print("\t", "CHIKV: ", len(chikv_epidemic_dset_dicts))
        print("\t", "Ebola: ", len(ebov_epidemic_dset_dicts))
        print("\t", "Zika: ", len(zikv_epidemic_dset_dicts))
        print("\t", "Infectious disease scenario: ", len(ids_dset_dicts))
        print("\t", "Mortality: ", len(mortality_dset_dicts))
        print("\t", "Surveillance: ", len(disease_surveillance_dset_dicts))
        print("\t", "Web: ", len(web_dset_dicts))
        print("\t", "Location: ", len(location_dset_dicts))