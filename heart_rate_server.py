from flask import Flask, jsonify, request


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
    if check_bad_input(patient) or check_bad_input(age):
        return "ERROR"
    else:
        return [patient, user, age]
