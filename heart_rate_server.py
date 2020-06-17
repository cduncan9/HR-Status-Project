from flask import Flask, jsonify, request
from datetime import datetime
import requests

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


def find_first_time(time_input, data):
    ref_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
    count = 0
    for time in data:
        temp = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        delta = ref_time-temp
        if delta.total_seconds >= 0:
            return count
        elif count == len(data):
            return "Time out of bounds"
        else:
            count = count + 1


def get_patient_heart_rates(patient_id, db):
    for patient in db:
        if patient_id == str(patient["patient_id"]):
            return patient["heart_rate"]
    return "Patient not found", 400


def find_patient(patient_id):
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            return patient
    return "Patient not found", 400


def get_patient_average_heart_rate(patient_id, db):
    data = get_patient_heart_rates(patient_id, db)
    if type(data) is not list:
        return "Patient not found", 400
    else:
        return sum(data) / len(data)


def read_heart_rate_info(in_dict):
    patient_id = in_dict['patient_id']
    heart_rate = in_dict['heart_rate']
    if type(patient_id) == str:
        patient_id = int(patient_id)
    if type(heart_rate) == str:
        heart_rate = int(heart_rate)
    return [patient_id, heart_rate]


def add_heart_rate_to_patient_db(hr_info, timestamp):
    pat_id = hr_info[0]
    pat_hr = hr_info[1]
    global patient_db
    for patient in patient_db:
        if patient['patient_id'] == pat_id:
            patient['heart_rate'].append(pat_hr)
            patient['timestamp'].append(timestamp)
            return True
    return "Error in adding heart rate info to database"


def current_time(time_input):
    # How can we test this
    time_string = datetime.strftime(time_input, "%Y-%m-%d %H:%M:%S")
    return time_string


def find_physician_email(patient_id):
    for attendant in attendant_db:
        if patient_id in attendant["patients"]:
            return attendant["attending_email"]
    return False


def send_email(hr_info, timestamp):
    # this email will make the POST request to email the physician
    server = "http://vcm-7631.vm.duke.edu:5007/hrss/send_email"
    email_content = ("Your patient with the patient_id number {} "
                     "had a tachycardic heart rate of {}"
                     " at the date/time {}".format(hr_info[0],
                                                   hr_info[1],
                                                   timestamp))
    physician_email = find_physician_email(hr_info[0])
    email_dict = {"from_email": "warning@hrsentinalserver.com",
                  "to_email": physician_email,
                  "subject": "PATIENT {} HAS TACHYCARDIA".format(hr_info[0]),
                  "content": email_content}
    r = requests.post(server, json=email_dict)
    return r.text


def check_heart_rate(hr_info, timestamp):
    age = 1
    for patient in patient_db:
        if patient['patient_id'] == hr_info[0]:
            age = patient['patient_age']
    if is_tachycardic(age, hr_info[1]):
        message_sent = send_email(hr_info, timestamp)
        return message_sent
    return True


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
    print(add_attendant_to_db(read_attending(in_dict), attendant_db))
    return "Attendant information stored", 200


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    in_dict = request.get_json()
    verify_input = verify_heart_rate_post(in_dict)
    if verify_input is not True:
        return verify_input, 400
    hr_info = read_heart_rate_info(in_dict)
    timestamp = current_time(datetime.now())
    add_heart_rate = add_heart_rate_to_patient_db(hr_info,
                                                  timestamp)
    if add_heart_rate is not True:
        return add_heart_rate, 400
    check_tachycardic = check_heart_rate(hr_info, timestamp)
    if check_tachycardic is not True:
        return check_tachycardic, 200
    print(patient_db)
    return "Heart rate information is stored", 200


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_patient_heart_data(patient_id):
    return jsonify(get_patient_heart_rates(patient_id, patient_db))


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_patient_avg_heart_rate(patient_id):
    return jsonify(get_patient_average_heart_rate(patient_id, patient_db))


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def get_interval_average():
    in_dict = request.get_json()
    patient_id = in_dict["patient_id"]
    time = in_dict["heart_rate_average_since"]
    patient = find_patient(patient_id)
    index = find_first_time(time, patient["timestamp"])
    return jsonify(sum(patient["heart_rate"][index:]) / len(patient["heart_rate"][index:]))


if __name__ == '__main__':
    app.run()
