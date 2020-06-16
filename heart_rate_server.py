from flask import Flask, jsonify, request
from datetime import datetime

patient_db = list()
attendant_db = list()

app = Flask(__name__)


def is_tachycardic(age, hr):
    if 1 <= age <= 2 and hr > 151:
        return True
    elif 3 < age <= 4 and hr > 137:
        return True
    elif 5 < age <= 7 and hr > 133:
        return True
    elif 8 < age <= 11 and hr > 130:
        return True
    elif 12 < age <= 15 and hr > 119:
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


def add_patient_to_db(info):
    new_patient_dict = {"patient_id": info[0], "attending_username": info[1],
                        "patient_age": info[2], "heart_rate": list(),
                        "timestamp": list(), "status": ""}
    patient_db.append(new_patient_dict)


def add_attendant_to_db(info, db):
    new_attendant_dict = {"attending_username": info[0],
                          "attending_email": info[1],
                          "attending_phone": info[2],
                          "patients": list()}
    db.append(new_attendant_dict)
    return db


def add_patient_to_attendant_db(info, db):
    patient_id = info[0]
    attendant_name = info[1]
    for attendant in db:
        if attendant["attending_username"] == attendant_name:
            attendant["patients"].append(patient_id)
            return False
    return True

def verify_heart_rate_post(in_dict):
    expected_keys = ("patient_id", "heart_rate")
    expected_values = (int, int)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty and check_bad_input(in_dict[key]):
            return "{} value is not the correct type".format(key)
    return True


def read_heart_rate_info(in_dict):
    patient_id = in_dict['patient_id']
    heart_rate = in_dict['heart_rate']
    if type(patient_id) == str:
        patient_id = int(patient_id)
    if type(heart_rate) == str:
        heart_rate = int(heart_rate)
    return [patient_id, heart_rate]


def add_heart_rate_to_patient_db(hr_info, timestamp, db):
    pat_id = hr_info[0]
    pat_hr = hr_info[1]
    for patient in db:
        if patient['patient_id'] == pat_id:
            patient['heart_rate'].append(pat_hr)
            patient['timestamp'].append(timestamp)
    return db


def current_time():
    time = datetime.now()
    time_string = datetime.strftime(time, "%Y-%m-%d %H:%M:%S")
    return time_string


# Put all of the route functions below this line
@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    in_dict = request.get_json()
    verify_input = verify_new_patient_info(in_dict)
    if verify_input is not True:
        return verify_input, 400
    patient_info = read_patient(in_dict)
    add_patient_to_db(patient_info)
    flag = add_patient_to_attendant_db(patient_info, attendant_db)
    if flag:
        return "Attendant does not exist", 400
    return "Patient information stored", 200


@app.route("/api/new_attending", methods=["POST"])
def post_new_attending():
    in_dict = request.get_json()
    print(add_patient_to_db(read_attending(in_dict)))
    return "Attendant information stored", 200


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    in_dict = request.get_json()
    verify_input = verify_heart_rate_post(in_dict)
    if verify_input is not True:
        return verify_input, 400
    hr_info = read_heart_rate_info(in_dict)
    timestamp = current_time()
    add_heart_rate = add_heart_rate_to_patient_db(hr_info,
                                                  timestamp,
                                                  patient_db)
    if add_heart_rate is not True:
        return add_heart_rate, 400
    return "Heart rate information is stored", 200


if __name__ == '__main__':
    app.run()
