from flask import Flask, jsonify, request


def is_tachycardic(age, hr):
    if 1 <= age <= 2 and hr > 151:
        return True
    elif 3 < age <= 4 and hr > 137:
        return True
    elif 5 < age <= 7 and hr > 133:
        return True
    elif 8 < age <= 11 and hr > 130:
        return True
    elif 12 < age <= 15 and hr > 199:
        return True
    elif 15 < age and hr > 100:
        return True
    else:
        return False


def check_bad_input(input):
    if type(input) == str:
        if not input.isdigit():
            return True
    return False


def read_attending(in_dict):
    user = in_dict["attending_username"]
    email = in_dict["attending_email"]
    phone = in_dict["attending_phone"]
    return [user, email, phone]


def read_patient(in_dict):
    patient = in_dict["patient_id"]
    user = in_dict["attending_username"]
    age = in_dict["patient_age"]
    if type(patient) == str:
        patient = int(patient)
    if type(age) == str:
        age = int(age)
    return [patient, user, age]


def verify_new_patient_info(in_dict):
    expected_keys = ("patient_id", "attending_username", "patient_age")
    expected_values = (int, str, int)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty and check_bad_input(in_dict[key]):
            return "{} value is not the correct type".format(key)
    return True


