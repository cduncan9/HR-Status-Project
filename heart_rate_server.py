from flask import Flask, jsonify, request
from datetime import datetime
import requests
import logging

patient_db = list()
attendant_db = list()

app = Flask(__name__)


def is_tachycardic(age, hr):
    '''determines based on age if heart rate is tachycardic

    Tachycardia is a heart condition in which the heart beats abnormally
    fast. The conditions for diagnosing tachycardia that were employed in
    this function were taken from "https://en.wikipedia.org/wiki/Tachycardia"

    :param age: int containing patient's age
    :param hr: int containin patient's heart rate

    :return: True if tachycardic and False if not tachycardic
    '''
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
    '''checks if input contains non-numeric characters

    Patient IDs can be input in strings or integers. If the
    type of the input is not a string, we know it is an integer
    and a valid patient ID. If it is a string we need to check if
    it contains any non-numeric characters which is done with
    .isdigit()

    :param input: str or in containing Patient ID

    :return: True if input is bad, False if input is good
    '''
    if type(input) == str:
        if not input.isdigit():
            return True
    return False


def read_attending(in_dict):
    '''Reads in attendant information from input dictionary

    The attendant information is input in a dictionary in the following
    format:
    {"attending_username": "Smith.J",
     "attending_email": "dr_user_id@yourdomain.com",
     "attending_phone": "919-867-5309}
    This function extracts each value from the dictionary

    :param in_dict: Dictionary containing attendant info
    :return: list containing attendant info
    '''
    user = in_dict["attending_username"]
    email = in_dict["attending_email"]
    phone = in_dict["attending_phone"]
    return [user, email, phone]


def read_patient(in_dict):
    '''Reads in patient information from input dictionary

    The attendant information is input in a dictionary in the following
    format:
    {"patient_id": 1, # usually this would be the patient MRN
     "attending_username": "Smith.J",
     "patient_age": 50, # in years}
    This function extracts each value from the dictionary

    :param in_dict: dictionary containing patient info
    :return: list containing patient info
    '''
    patient = in_dict["patient_id"]
    user = in_dict["attending_username"]
    age = in_dict["patient_age"]
    if type(patient) == str:
        patient = int(patient)
    if type(age) == str:
        age = int(age)
    return [patient, user, age]


def add_patient_to_db(info):
    '''Creates a patient dictionary and adds it to database

    Patient info is input as a list and dictionary is created
    containing all the required keys specified on GitHub which
    is then added to the global patient database variable

    :param info: list containing patient info
    '''
    new_patient_dict = {"patient_id": info[0], "attending_username": info[1],
                        "patient_age": info[2], "heart_rate": list(),
                        "timestamp": list(), "status": ""}
    patient_db.append(new_patient_dict)


def add_attendant_to_db(info, db):
    '''Creates an attendant dictionary and adds it to database

    Attendant info is input as a list and dictionary is created
    containing all the required keys specified on GitHub which
    is then added to the global attendant database variable

    :param info: list containing attendant info
    :param db: list containing attendant dictionaries
    '''
    new_attendant_dict = {"attending_username": info[0],
                          "attending_email": info[1],
                          "attending_phone": info[2],
                          "patients": list()}
    db.append(new_attendant_dict)
    return db


def add_patient_to_attendant_db(info, db):
    '''Adds patient ID to corresponding attendant's list of patients

    This method looks through the list of attendant dictionaries for
    the input patient's attendant. If the attendant is found the patient's
    ID is appended to the attendant's list of patients.

    :param info: list of patient info
    :param db: list of attendant dictionaries
    :return: False if patient's attendant is found, True if patients's
             attendant not found
    '''
    patient_id = info[0]
    attendant_name = info[1]
    for attendant in db:
        if attendant["attending_username"] == attendant_name:
            attendant["patients"].append(patient_id)
            return False
    return True


def find_first_time(time_input, data):
    '''Finds first time in list of timestamps equal to or after input timestamp

    This method is used for the interval average route. The first index of the
    heart rate data list that occurs at or after the input timestamp
    must be found. This function finds that index.

    :param time_input: datetime object containing input timestamp
    :param data: list of patient heart rate timestamps

    :return: int containing first index of interval
    '''
    ref_time = datetime.strptime(time_input, "%Y-%m-%d %H:%M:%S")
    count = 0
    for time in data:
        temp = datetime.strptime(time, "%Y-%m-%d %H:%M:%S")
        delta = ref_time-temp
        if delta.total_seconds() <= 0:
            return count
        elif count == len(data):
            return "Time out of bounds"
        else:
            count = count + 1


def get_patient_heart_rates(patient_id, db):
    '''Returns list of patient heart rate data

    This method takes in the patient ID and patient database and
    outputs the list of the specified patient's heart rate data.

    :param patient_id: int containing patient ID
    :param db: list of patient dictionaries
    :return: list of patient heart rate data, str "Patient not found" and
             error 400 if not found
    '''
    for patient in db:
        if patient_id == str(patient["patient_id"]):
            return patient["heart_rate"]
    return "Patient not found", 400


def find_patient(patient_id, db):
    '''Returns specified patient dictionary

    This method takes in the patient ID and patient database and
    outputs the dictionary containing the specified patient's info.

    :param patient_id: int containing patient ID
    :param db: list of patient dictionaries
    :return: dictionary of patient data, str "Patient not found" and
             error 400 if patient not found
    '''
    for patient in db:
        if patient["patient_id"] == patient_id:
            return patient
    return "Patient not found", 400


def get_patient_average_heart_rate(patient_id, db):
    '''Returns the average of the patient's heart rate data

    This method takes in the patient ID and patient database and
    outputs the specified patient's average heart rate.

    :param patient_id: int containing patient ID
    :param db: list of patient dictionaries
    :return: int containing patient's average heart rate data,
             str "Patient not found" and error 400 if not found
    '''
    data = get_patient_heart_rates(patient_id, db)
    if type(data) is not list:
        return "Patient not found", 400
    else:
        return sum(data) / len(data)


def read_heart_rate_info(in_dict):
    '''Reads in patient ID and heart rate

    A patient dictionary is input into this function and the
    patient id and heart rate data are output in a list

    :param in_dict: dictionary containing patient data
    :return: list containing patient ID and list of heart rates
    '''
    patient_id = in_dict['patient_id']
    heart_rate = in_dict['heart_rate']
    if type(patient_id) == str:
        patient_id = int(patient_id)
    if type(heart_rate) == str:
        heart_rate = int(heart_rate)
    return [patient_id, heart_rate]


def add_heart_rate_to_patient_db(hr_info, timestamp):
    '''Adds patient heart rate to database

    Takes in patient heart rate info and timestamp and adds
    heart rate data and timestamp to patient's dictionary

    :param hr_info: list containing patient ID and heart rate data point
    :param timestamp: str containing timestamp following format on GitHub

    :return: True if patient found and info added,
             str "Error in adding hear rate info to database" otherwise
    '''
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
    '''Turns input datetime object into a string

    :param time_input: datetime object
    :return: str of datetime object
    '''
    # How can we test this
    time_string = datetime.strftime(time_input, "%Y-%m-%d %H:%M:%S")
    return time_string


def find_physician_email(patient_id):
    '''Finds patient's physician email

    :param patient_id: int containing patient ID
    :return: str containing attendant email if attendant found,
             False otherwise
    '''
    for attendant in attendant_db:
        if patient_id in attendant["patients"]:
            return attendant["attending_email"]
    return False


def send_email(hr_info, timestamp):
    '''Sends email using server to attendant if patient is tachycardic

    If a tachycardic event occurs to a patient, this method creates and
    sends an email to that patient's attendant saying they have tachycardia.

    :param hr_info: list containing patient ID and heart rate data point
    :param timestamp: str containing timestamp

    :return: str containing email text if email sent,
             str "Physician not in database" error 400 otherwise
    '''
    # this email will make the POST request to email the physician
    server = "http://vcm-7631.vm.duke.edu:5007/hrss/send_email"
    email_content = ("Your patient with the patient_id number {} "
                     "had a tachycardic heart rate of {}"
                     " at the date/time {}".format(hr_info[0],
                                                   hr_info[1],
                                                   timestamp))
    physician_email = find_physician_email(hr_info[0])
    if physician_email is False:
        return "Physician not in database", 400
    email_dict = {"from_email": "warning@hrsentinalserver.com",
                  "to_email": physician_email,
                  "subject": "PATIENT {} HAS TACHYCARDIA".format(hr_info[0]),
                  "content": email_content}
    r = requests.post(server, json=email_dict)
    return r.text


def check_heart_rate(hr_info, timestamp):
    '''Checks heart rate and sends email if tachycardic

    Checks heart rate for tachyrcardia by callin is_tachycardic function
    and send email by calling send_email function.

    :param hr_info: list containing int patient ID and
                    int heart rate data point
    :param timestamp: str containing timestamp
    :return: str of email text if email sent,
             True otherwise
    '''
    age = 1
    for patient in patient_db:
        if patient['patient_id'] == hr_info[0]:
            age = patient['patient_age']
            patient["status"] = "not tachycardic"
    if is_tachycardic(age, hr_info[1]):
        message_sent = send_email(hr_info, timestamp)
        for patient in patient_db:
            if patient['patient_id'] == hr_info[0]:
                patient["status"] = "tachycardic"
        return message_sent
    return True


def get_patient_status(patient_id):
    '''Outputs dictionary containing patient status

    This function takes in a patinent ID, finds them in the patient
    database, and builds a containing the status information which
    is then output.

    :param patient_id: int containing patient ID
    :return: dictionary of patient status if patient found,
             str "Patient not found" if patient not found
    '''
    patient_id = int(patient_id)
    for patient in patient_db:
        if patient["patient_id"] == patient_id:
            heart_rate = patient['heart_rate']
            if len(heart_rate) == 1:
                heart_rate = heart_rate[0]
            else:
                heart_rate = heart_rate[-1]
            status = patient['status']
            timestamp = patient['timestamp']
            if len(timestamp) == 1:
                timestamp = timestamp[0]
            else:
                timestamp = timestamp[-1]
            status_dict = {"heart_rate": heart_rate,
                           "status": status,
                           "timestamp": timestamp}
            return status_dict
    return "Patient not found"


def get_patient_id_list(attending_username):
    '''Returns attendant's list of patients

    :param attending_username: str containing attendant username
    :return: list of ints containing patient IDs
    '''
    for attendant in attendant_db:
        if attendant["attending_username"] == attending_username:
            return attendant["patients"]


def patients_for_attending_username(patient_id_list):
    '''Takes in list of patients and builds a list of dictionaries

    Builds list of dictionaries of the following format:
    {"patient_id": patient["patient_id"],
     "last_heart_rate": last_heart_rate,
     "last_time": last_time,
     "status": patient["status"]}
     from an input list of integers containing patient IDs

    :param patient_id_list: list of ints containing patient IDs
    :return: list of dictionaries containing patient info
             in the above format
    '''
    patients_list = list()
    for patient in patient_db:
        if patient["patient_id"] in patient_id_list:
            last_heart_rate = patient["heart_rate"]
            if len(last_heart_rate) == 1:
                last_heart_rate = last_heart_rate[0]
            else:
                last_heart_rate = last_heart_rate[-1]
            last_time = patient["timestamp"]
            if len(last_time) == 1:
                last_time = last_time[0]
            else:
                last_time = last_time[-1]
            temp_dict = {"patient_id": patient["patient_id"],
                         "last_heart_rate": last_heart_rate,
                         "last_time": last_time,
                         "status": patient["status"]}
            patients_list.append(temp_dict)
    return patients_list


# Verification functions under this line
def verify_new_attending(in_dict):
    """
    This function verifies the input information for post_new_attending()

    This function receives the dictionary containing the input
    from the function post_new_attending(). The function uses a for
    loop to check if the key strings are the same as the expected
    key strings and that the value types are the same as
    the expected value types. If the keys are incorrect, then a
    string notifying the client that a key is missing is returned.
    If a value type is incorrect, then a string is returned
    to the patient saying that a specific value is of the wrong type.
    If nothing is wrong, then this function returns True.
    :param in_dict: a dictionary sent from the client
    :return: True if the dictionary has the correct keys and value
    types and a string explaining why the dictionary is wrong
    otherwise.
    """
    expected_keys = ("attending_username", "attending_email",
                     "attending_phone")
    expected_values = (str, str, str)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty:
            return "{} value is not the correct type".format(key)
    return True


def verify_internal_average(in_dict):
    """This function verifies the input information for post_interval_average()

    This function receives the dictionary containing the input
    from the function post_interval_average(). The function uses a for
    loop to check if the key strings are the same as the expected
    key strings and that the value types are the same as
    the expected value types. If the keys are incorrect, then a
    string notifying the client that a key is missing is returned.
    If a value type is incorrect, then the function
    check_if_bad_input() is called to see if a value contains a
    numeric string. If this too fails, then a string is returned
    to the patient saying that a specific value is of the wrong type.
    If nothing is wrong, then this function returns True.
    :param in_dict: a dictionary sent from the client
    :return: True if the dictionary has the correct keys and value
    types and a string explaining why the dictionary is wrong
    otherwise."""
    expected_keys = ("patient_id", "heart_rate_average_since")
    expected_values = (int, str)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty and check_bad_input(in_dict[key]):
            return "{} value is not the correct type".format(key)
    return True


def verify_attendant_exists(attending_username):
    """
    This function verifies that a dictionary with the
    attending_username exists in attending_db

    This function receives the attending_username as
    input and uses a for loop to see if any of the stored
    physician information in the attending_db has the
    attending_username sent as the input. If there is one,
    Then this function returns true. If not, then this function
    returns a string notifying the client.
    :param attending_username: the username of a physician
    :return: True if a dictionary exists that has the
    attending_username, or a string explaining otherwise
    """
    for attendant in attendant_db:
        if attendant["attending_username"] == attending_username:
            return True
    return "The physician does not exist in database"


def verify_heart_rate_post(in_dict):
    """This function verifies the input information for post_heart_rate()

    This function receives the dictionary containing the input
    from the function post_heart_rate(). The function uses a for
    loop to check if the key strings are the same as the expected
    key strings and that the value types are the same as
    the expected value types. If the keys are incorrect, then a
    string notifying the client that a key is missing is returned.
    If a value type is incorrect, then the function
    check_if_bad_input() is called to see if a value contains a
    numeric string. If this too fails, then a string is returned
    to the patient saying that a specific value is of the wrong type.
    If nothing is wrong, then this function returns True.
    :param in_dict: a dictionary sent from the client
    :return: True if the dictionary has the correct keys and value
    types and a string explaining why the dictionary is wrong
    otherwise."""
    expected_keys = ("patient_id", "heart_rate")
    expected_values = (int, int)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty and check_bad_input(in_dict[key]):
            return "{} value is not the correct type".format(key)
    return True


def verify_new_patient_info(in_dict):
    """This function verifies the input information for post_new_patient()

    This function receives the dictionary containing the input
    from the function post_new_patient(). The function uses a for
    loop to check if the key strings are the same as the expected
    key strings and that the value types are the same as
    the expected value types. If the keys are incorrect, then a
    string notifying the client that a key is missing is returned.
    If a value type is incorrect, then the function
    check_if_bad_input() is called to see if a value contains a
    numeric string. If this too fails, then a string is returned
    to the patient saying that a specific value is of the wrong type.
    If nothing is wrong, then this function returns True.
    :param in_dict: a dictionary sent from the client
    :return: True if the dictionary has the correct keys and value
    types and a string explaining why the dictionary is wrong
    otherwise."""
    expected_keys = ("patient_id", "attending_username", "patient_age")
    expected_values = (int, str, int)
    for key, ty in zip(expected_keys, expected_values):
        if key not in in_dict.keys():
            return "{} key not found in input".format(key)
        if type(in_dict[key]) != ty and check_bad_input(in_dict[key]):
            return "{} value is not the correct type".format(key)
    return True


# Put all of the route functions below this line
@app.route("/api/new_patient", methods=["POST"])
def post_new_patient():
    """This function stores a new patient's information in patient_db

    This function receives a POST request from a client that has
    a dictionary containing patient information. The dictionary
    includes the patient_id, attending_username, and patient_age.
    This function first verifies that the dictionary sent has
    the correct key names and value types. If the input data
    is not correct, then an error string and a status code of 400
    is returned to the client. Then the function attempts to send
    the patient_id to be stored in their attending physician's
    database. If their is no attending physician with the code
    given in the input dictionary then the function will return
    the proper error message and the status code of 400. If the
    patient is  successfully added to the patient_db and
    attendant_db then a status code of 200 is returned.

    :return: A string saying whether the patient was added or if
    there was an error and a corresponding status code
    """
    in_dict = request.get_json()
    verify_input = verify_new_patient_info(in_dict)
    if verify_input is not True:
        return verify_input, 400
    patient_info = read_patient(in_dict)
    flag = add_patient_to_attendant_db(patient_info, attendant_db)
    if flag:
        return "Attendant does not exist", 400
    add_patient_to_db(patient_info)
    print(patient_db)
    logging.info("New patient added... " + "Patient ID: " +
                 str(in_dict["patient_id"]) + "\n")
    return "Patient information stored", 200


@app.route("/api/new_attending", methods=["POST"])
def post_new_attending():
    """
    This function stores the physician information

    This function receives a POST request from a client that has
    a dictionary containing attending physician information.
    The dictionary includes the attending_username,
    attending_email, and attending_phone.
    This function first verifies that the dictionary sent has
    the correct key names and value types. If the input data
    is not correct, then an error string and a status code of 400
    is returned to the client. Then the function attempts to send
    the attending physician information to the attending_db. If the
    patient is  successfully added to the attendant_db then
    a status code of 200 is returned.

    :return: A string saying whether the attending physician
     was added or if there was an error and a corresponding
     status code
    """
    in_dict = request.get_json()
    verify_input = verify_new_attending(in_dict)
    if verify_input is not True:
        return verify_input, 400
    print(add_attendant_to_db(read_attending(in_dict), attendant_db))
    logging.info("New attendant added... Username: " +
                 in_dict["attending_username"] + ", email: " +
                 in_dict["attending_email"] + "\n")
    return "Attendant information stored", 200


@app.route("/api/heart_rate", methods=["POST"])
def post_heart_rate():
    """
    This function stores a heart rate and timestamp for a patient

    This function receives a dictionary containing a patient_id and
    a heart_rate. This function first verifies that the dictionary sent has
    the correct key names and value types. If the input data
    is not correct, then an error string and a status code of 400
    is returned to the client. Then this function stores the current
    time in a datetime object. This function calls the function
    current_time which converts the datetime object to a string.
    The heart_rate and timestamp are then added to the database for
    the dictionary with the corresponding patient_id. If there is no
    such patient_id then an error is returned. Then this function
    calls the function check_heart_rate(). If the heart_rate is
    tachycardic then the function check_heart_rate() will trigger
    an email being sent to the patient's attending physician, and
    a string will be returned to the client notifying them of this.

    :return: A string signaling if the heart rate is
     properly added to the database. If the heart rate is tachycardic,
     then a string signaling that an email was sent to the physician is
     returned.
    """
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
        patient = find_patient(hr_info[0], patient_db)
        logging.info("Tachycardic Heart Beat Detected..." +
                     "Patient ID: " + str(hr_info[0]) + ", " +
                     "Heart Rate: " + str(hr_info[1]) + ", " +
                     "Attending Physician: " +
                     patient["attending_username"] + "\n")
        return check_tachycardic, 200
    print(patient_db)
    return "Heart rate information is stored", 200


@app.route("/api/heart_rate/<patient_id>", methods=["GET"])
def get_patient_heart_data(patient_id):
    """
    This function returns a list of heart rates for a patient.

    This function is for a GET request and receives a patient_id
    as part of a variable URL. The function gets the list of
    heart_rate for the corresponding patient_id and sends it to a
    client in a JSON format.

    :param patient_id: a number corresponding to a patient in patient_db
    :return: list of heart rates for that patient
    """
    return jsonify(get_patient_heart_rates(patient_id, patient_db))


@app.route("/api/heart_rate/average/<patient_id>", methods=["GET"])
def get_patient_avg_heart_rate(patient_id):
    """
    This function returns the average heart_rate for a patient

    This function is for a GET request and receives a patient_id
    as part of a variable URL. The function gets the average
    heart_rate for the corresponding patient_id and sends it to a
    client in a JSON format.
    :param patient_id: a number corresponding to a patient in patient_db
    :return: a float of the average heart_rate for a patient
    """
    return jsonify(get_patient_average_heart_rate(patient_id, patient_db))


@app.route("/api/status/<patient_id>", methods=["GET"])
def get_status(patient_id):
    """
    This function returns the status of a patient

    This function is for a GET request and receives a patient_id
    as part of a variable URL. The function returns a dictionary
    containing the most recent heart_rate, timestamp, and the
    status for the corresponding patient_id and sends it to a
    client in a JSON format.
    :param patient_id: a number corresponding to a patient in patient_db
    :return: a dictionary containing the most recent heart_rate,
    timestamp, and the status
    """
    return jsonify(get_patient_status(patient_id))


@app.route("/api/heart_rate/interval_average", methods=["POST"])
def post_interval_average():
    """
    This function returns the average heart rate for a patient_id
    from a specific time

    This function receives a POST request containing the keys
    patient_id, and heart_rate_average_since. This function
    first verifies that the keys and values are correct, and
    returns an error string if not. Then this function calls
    the function find_patient() which returns patient info for
    the patient_id. The function then finds the average heart_rate
    for all readings from the time specified by the input dictionary.
    :return: a float giving the average heart_rate since the time specified
    """
    in_dict = request.get_json()
    verify_input = verify_internal_average(in_dict)
    if verify_input is not True:
        return verify_input, 400
    print(in_dict)
    patient_id = in_dict["patient_id"]
    print(patient_id)
    time = in_dict["heart_rate_average_since"]
    patient = find_patient(int(patient_id), patient_db)
    index = find_first_time(time, patient["timestamp"])
    answer = sum(patient["heart_rate"]
                 [index:]) / len(patient["heart_rate"][index:])
    return jsonify(answer)


@app.route("/api/patients/<attending_username>", methods=["GET"])
def get_patients_for_attending_username(attending_username):
    """
    This function returns a list of patient information for a
    specific physician

    This function is for a GET request and receives an attending_username
    as part of a variable URL. This function first checks to see if the
    attending_username is stored in the database. If the
    attending_username is not in the database then a string is returned
    notifying the client. Then this function calls a function that gets
    the list of patient_id for the attending_username. For each
    patient_id, a dictionary is stored in a list that contains the
    patient_id, last_heart_rate, last_time, and status. This list
    of patient dictionaries is then returned to the client.
    :param attending_username: the username used by a physician
    :return: a list containing dictionaries of patient information
    """
    verify_attendant = verify_attendant_exists(attending_username)
    if verify_attendant is not True:
        return verify_attendant, 400
    patient_id_list = get_patient_id_list(attending_username)
    return jsonify(patients_for_attending_username(patient_id_list))


if __name__ == '__main__':
    logging.basicConfig(filename="code_status.log", filemode='w',
                        level=logging.DEBUG)
    app.run()
