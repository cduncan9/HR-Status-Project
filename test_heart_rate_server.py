import pytest
import numpy as np
from datetime import datetime


@pytest.mark.parametrize("age, hr, expected",
                         [(1, 170, True),
                          (2, 150, False),
                          (18, 120, True),
                          (5, 5, False),
                          (9, 135, True)])
def test_is_tachycardic(age, hr, expected):
    from heart_rate_server import is_tachycardic
    answer = is_tachycardic(age, hr)
    assert answer == expected


@pytest.mark.parametrize("data, expected",
                         [(123, False),
                          ("123", False),
                          ("abc123", True)])
def test_check_bad_input(data, expected):
    from heart_rate_server import check_bad_input
    answer = check_bad_input(data)
    assert answer == expected


@pytest.mark.parametrize("data, expected",
                         [({"patient_id": 1,
                            "attending_username": "Canyon.D",
                            "patient_age": 20}, [1, "Canyon.D", 20]),
                          ({"patient_id": 123,
                            "attending_username": "Aidan.T",
                            "patient_age": 21}, [123, "Aidan.T", 21]),
                          ({"patient_id": "1",
                            "attending_username": "Canyon.D",
                            "patient_age": 20}, [1, "Canyon.D", 20]),
                          ({"patient_id": 5,
                            "attending_username": "Canyon.D",
                            "patient_age": "20"}, [5, "Canyon.D", 20])])
def test_read_patient(data, expected):
    from heart_rate_server import read_patient
    answer = read_patient(data)
    assert answer == expected


@pytest.mark.parametrize("data, expected",
                         [({"attending_username": "John.J",
                            "attending_email": "john.j@gmail.com",
                            "attending_phone": "919-289-5445"},
                           ["John.J", "john.j@gmail.com", "919-289-5445"]),
                          ({"attending_username": "Giannis.A",
                            "attending_email": "giannis.a@bucks.net",
                            "attending_phone": "287-987-0098"},
                           ["Giannis.A", "giannis.a@bucks.net",
                            "287-987-0098"])])
def test_read_attending(data, expected):
    from heart_rate_server import read_attending
    answer = read_attending(data)
    assert answer == expected


@pytest.mark.parametrize("info, db, expected",
                         [([1, "Canyon.D", 20],
                           [{"attending_username": "Canyon.D",
                             "attending_email": "john.j@gmail.com",
                             "attending_phone": "919-289-5445",
                             "patients": [5]}],
                           False),
                          ([1, "Canyon.D", 20],
                           [{"attending_username": "Giannis.A",
                             "attending_email": "giannis.a@bucks.net",
                             "attending_phone": "287-987-0098",
                             "patients": [20]}],
                           True)])
def test_add_patient_to_attendant_db(info, db, expected):
    from heart_rate_server import add_patient_to_attendant_db
    answer = add_patient_to_attendant_db(info, db)
    assert answer == expected


@pytest.mark.parametrize("info, db, expected",
                         [(["Canyon.D", "canyon@duke.edu", "919-200-8973"],
                           [{"attending_username": "John.D",
                             "attending_email": "john.j@gmail.com",
                             "attending_phone": "919-289-5445",
                             "patients": [5]}],
                           [{"attending_username": "John.D",
                             "attending_email": "john.j@gmail.com",
                             "attending_phone": "919-289-5445",
                             "patients": [5]},
                            {"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": []}]),
                          (["Canyon.D", "canyon@duke.edu", "919-200-8973"],
                           [],
                           [{"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": []}])])
def test_add_attendant_to_db(info, db, expected):
    from heart_rate_server import add_attendant_to_db
    answer = add_attendant_to_db(info, db)
    assert answer == expected


@pytest.mark.parametrize("data, expected",
                         [({"patient_id": 1,
                            "attending_username": "Canyon.D",
                            "patient_age": 20}, True),
                          ({"patient_id": 123,
                            "attending_username": "Aidan.T",
                            "patient_age": '21'}, True),
                          ({"patient_id": '123',
                            "attending_username": "Aidan.T",
                            "patient_age": 21}, True),
                          ({"patient_id": 1,
                            "attending_username": "Canyon.D",
                            "age": 20}, "patient_age key not found in input"),
                          ({"patient_id": '123',
                            "attending_username": "Aidan.T",
                            "patient_age": "Twenty One"},
                           "patient_age value is not the correct type")])
def test_verify_new_patient_info(data, expected):
    from heart_rate_server import verify_new_patient_info
    answer = verify_new_patient_info(data)
    assert answer == expected


@pytest.mark.parametrize("data, expected",
                         [({'patient_id': 1,
                            'heart_rate': 100}, True),
                          ({'patient_id': '1',
                            'heart_rate': 100}, True),
                          ({'patient_id': 1,
                            'heart_rate': '100'}, True),
                          ({'patientID': 1,
                            'heart_rate': 100},
                           "patient_id key not found in input"),
                          ({'patient_id': 'One',
                            'heart_rate': '100'},
                           'patient_id value is not the correct type')])
def test_verify_heart_rate_post(data, expected):
    from heart_rate_server import verify_heart_rate_post
    answer = verify_heart_rate_post(data)
    assert answer == expected


@pytest.mark.parametrize('data, expected',
                         [({'patient_id': 1,
                            'heart_rate': 100}, [1, 100]),
                          ({'patient_id': '1',
                            'heart_rate': 100}, [1, 100]),
                          ({'patient_id': 1,
                            'heart_rate': '100'}, [1, 100])])
def test_read_heart_rate_info(data, expected):
    from heart_rate_server import read_heart_rate_info
    answer = read_heart_rate_info(data)
    assert answer == expected


@pytest.mark.parametrize('hr_info, timestamp, db, expected',
                         [([1, 100], '2018-03-09 11:00:36',
                           [{"patient_id": 1,
                             "attending_username": 'Therien.A',
                             "patient_age": 21, "heart_rate": list(),
                             "timestamp": list(), "status": ""}], True),
                          ([100, 200], '2018-03-09 11:00:36',
                           [{"patient_id": 2,
                             "attending_username": 'Duncan.C',
                             "patient_age": 21, "heart_rate": list(),
                             "timestamp": list(), "status": ""}],
                           "Error in adding heart rate info to database"),
                          ([0, 100], '2018-03-09 11:00:36', [],
                           "Error in adding heart rate info to database")])
def test_add_heart_rate_to_patient_db(hr_info, timestamp, db, expected):
    from heart_rate_server import add_heart_rate_to_patient_db, patient_db
    for patient in db:
        patient_db.append(patient)
    answer = add_heart_rate_to_patient_db(hr_info, timestamp)
    assert answer == expected


@pytest.mark.parametrize("hr_info, timestamp, pat_db, att_db, expected",
                         [([1, 100], '2018-03-09 11:00:36',
                           [{"patient_id": 1,
                             "attending_username": 'Therien.A',
                             "patient_age": 21, "heart_rate": list(),
                             "timestamp": list(), "status": ""}],
                           [{"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [20]}], True),
                          ([20, 200], '2018-03-09 11:00:36',
                           [{"patient_id": 20, "attending_username": 'Duncan.C',
                             "patient_age": 21, "heart_rate": list(),
                             "timestamp": list(), "status": ""}],
                           [{"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [20]}],
                           'E-mail sent to canyon@duke.edu'
                           ' from warning@hrsentinalserver.com'),
                          ([201, 200], '2018-03-09 11:00:36',
                           [{"patient_id": 201,
                             "attending_username": 'Duncan.C',
                             "patient_age": 21, "heart_rate": list(),
                             "timestamp": list(), "status": ""}],
                           [{"attending_username": "Canyon.D",
                             "attending_email": "",
                             "attending_phone": "919-200-8973",
                             "patients": [201]}],
                           "'to_email' is not a correct e-mail address")
                          ])
def test_check_heart_rate(hr_info, timestamp, pat_db, att_db, expected):
    from heart_rate_server import check_heart_rate, patient_db, attendant_db
    for attendant in att_db:
        attendant_db.append(attendant)
    for patient in pat_db:
        patient_db.append(patient)
    answer = check_heart_rate(hr_info, timestamp)
    assert answer == expected


@pytest.mark.parametrize("patient_id, db, expected",
                         [("1", [{"patient_id": 1,
                                  "attending_username": 'Therien.A',
                                  "patient_age": 21, "heart_rate": [120],
                                  "timestamp": list(), "status": ""},
                                 {"patient_id": 2,
                                  "attending_username": 'Therien.A',
                                  "patient_age": 21, "heart_rate": [100],
                                  "timestamp": list(), "status": ""}],
                           [120]), ("4", [{"patient_id": 1,
                                           "attending_username": 'Therien.A',
                                           "patient_age": 21, "heart_rate": [120],
                                           "timestamp": list(), "status": ""},
                                          {"patient_id": 2,
                                           "attending_username": 'Therien.A',
                                           "patient_age": 21, "heart_rate": [100],
                                           "timestamp": list(), "status": ""}],
                                    ('Patient not found', 400))])
def test_get_patient_heart_rates(patient_id, db, expected):
    from heart_rate_server import get_patient_heart_rates
    answer = get_patient_heart_rates(patient_id, db)
    assert answer == expected


@pytest.mark.parametrize("patient_id, db, expected",
                         [(106, [{"patient_id": 106,
                                  "attending_username": 'Therien.A',
                                  "patient_age": 21, "heart_rate": [120],
                                  "timestamp": list(), "status": ""},
                                 {"patient_id": 107,
                                  "attending_username": 'Therien.A',
                                  "patient_age": 21, "heart_rate": [100],
                                  "timestamp": list(), "status": ""}],
                           {"patient_id": 106,
                            "attending_username": 'Therien.A',
                            "patient_age": 21, "heart_rate": [120],
                            "timestamp": list(), "status": ""}
                           ), (111, [{"patient_id": 1,
                                      "attending_username": 'Therien.A',
                                      "patient_age": 21, "heart_rate": [120],
                                      "timestamp": list(), "status": ""},
                                     {"patient_id": 2,
                                      "attending_username": 'Therien.A',
                                      "patient_age": 21, "heart_rate": [100],
                                      "timestamp": list(), "status": ""}],
                               ('Patient not found', 400))])
def test_find_patient(patient_id, db, expected):
    from heart_rate_server import find_patient
    answer = find_patient(patient_id, db)
    assert answer == expected


def test_current_time():
    from heart_rate_server import current_time
    time_input = datetime(2018, 3, 9, 11, 0, 36)
    answer = current_time(time_input)
    expected = '2018-03-09 11:00:36'
    assert answer == expected


@pytest.mark.parametrize("patient_id, db, expected",
                         [(1, [{"attending_username": "Canyon.D",
                                "attending_email": "canyon@duke.edu",
                                "attending_phone": "919-200-8973",
                                "patients": [1]},
                               {"attending_username": "Aidan.T",
                                "attending_email": "aidan@duke.edu",
                                "attending_phone": "919-200-8973",
                                "patients": [2]}], "canyon@duke.edu"),
                          (2, [], "aidan@duke.edu"),
                          (315, [], False)])
def test_find_physician_email(patient_id, db, expected):
    from heart_rate_server import find_physician_email, attendant_db
    for attendant in db:
        attendant_db.append(attendant)
    answer = find_physician_email(patient_id)
    assert answer == expected


@pytest.mark.parametrize("patient_id, db, expected",
                         [(1002, [{"patient_id": 1000,
                                   "attending_username": 'Therien.A',
                                   "patient_age": 21,
                                   "heart_rate": [70, 65],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "not tachycardic"},
                                  {"patient_id": 1002,
                                   "attending_username": 'Duncan.C',
                                   "patient_age": 21,
                                   "heart_rate": [60, 150],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "tachycardic"},
                                  {"patient_id": 1003,
                                   "attending_username": 'Bob.D',
                                   "patient_age": 40,
                                   "heart_rate": [90, 80],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:01:36'],
                                   "status": "not tachycardic"},
                                  {"patient_id": 1004,
                                   "attending_username": 'Williamson.Z',
                                   "patient_age": 19,
                                   "heart_rate": [70, 105],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "tachycardic"}],
                           {"heart_rate": 150, "status": "tachycardic",
                            "timestamp": '2020-03-10 11:00:36'}),
                          (1003, [{"patient_id": 1005,
                                   "attending_username": 'Therien.A',
                                   "patient_age": 21,
                                   "heart_rate": [70, 65],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "not tachycardic"},
                                  {"patient_id": 1006,
                                   "attending_username": 'Duncan.C',
                                   "patient_age": 21,
                                   "heart_rate": [60, 150],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "tachycardic"},
                                  {"patient_id": 1007,
                                   "attending_username": 'Bob.D',
                                   "patient_age": 40,
                                   "heart_rate": [90, 80],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:01:36'],
                                   "status": "not tachycardic"},
                                  {"patient_id": 1008,
                                   "attending_username": 'Williamson.Z',
                                   "patient_age": 19,
                                   "heart_rate": [70, 105],
                                   "timestamp": ['2020-03-09 11:00:36',
                                                 '2020-03-10 11:00:36'],
                                   "status": "tachycardic"}],
                           {"heart_rate": 80, "status": "not tachycardic",
                            "timestamp": '2020-03-10 11:01:36'}
                           ), (1019, [], "Patient not found")])
def test_get_patient_status(patient_id, db, expected):
    from heart_rate_server import patient_db, get_patient_status
    for patient in db:
        patient_db.append(patient)
    answer = get_patient_status(patient_id)
    assert answer == expected


@pytest.mark.parametrize("time, times, expected",
                         [("2018-03-09 11:00:36",
                           ["2018-03-09 10:00:36", "2018-03-09 11:00:36",
                            "2018-03-09 11:00:36"],
                           1),
                          ("2018-03-09 11:00:36",
                           ["2018-03-09 10:00:36", "2018-03-09 11:00:25",
                            "2018-03-09 11:00:37", "2018-03-09 11:00:38"],
                           2),
                          ("2018-03-09 11:00:36",
                           ["2018-03-09 11:00:36"],
                           0),
                          ("2018-03-09 11:00:36",
                           ["2018-03-09 11:00:16", "2018-03-09 11:00:26",
                            "2018-03-09 11:00:36"],
                           2)])
def test_find_first_time(time, times, expected):
    from heart_rate_server import find_first_time
    answer = find_first_time(time, times)
    assert answer == expected


@pytest.mark.parametrize("attending_username, db, expected",
                         [("Canyon.D",
                           [{"attending_username": "Aidan.T",
                             "attending_email": "aidan@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [500, 501]},
                            {"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [502]},
                            {"attending_username": "Bob.D",
                             "attending_email": "robert@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [503, 504, 505]},
                            {"attending_username": "Zion.W",
                             "attending_email": "Zion@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": []}], True),
                          ("Max.G", [],
                           "The physician does not exist in database"),
                          ("Zion.W", [], True)])
def test_verify_attendant_exists(attending_username, db, expected):
    from heart_rate_server import verify_attendant_exists, attendant_db
    for attendant in db:
        attendant_db.append(attendant)
    answer = verify_attendant_exists(attending_username)
    assert answer == expected


@pytest.mark.parametrize("attending_username, db, expected",
                         [("Bob.D",
                           [{"attending_username": "Aidan.T",
                             "attending_email": "aidan@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [500, 501]},
                            {"attending_username": "Canyon.D",
                             "attending_email": "canyon@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [502]},
                            {"attending_username": "Bob.D",
                             "attending_email": "robert@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": [503, 504, 505]},
                            {"attending_username": "Zion.W",
                             "attending_email": "Zion@duke.edu",
                             "attending_phone": "919-200-8973",
                             "patients": []}], [503, 504, 505]),
                          ("Zion.W", [], [])])
def test_get_patient_id_list(attending_username, db, expected):
    from heart_rate_server import get_patient_id_list, attendant_db
    for attendant in db:
        attendant_db.append(attendant)
    answer = get_patient_id_list(attending_username)
    assert answer == expected


@pytest.mark.parametrize("patient_id_list, pat_db, expected",
                         [([602, 603],
                           [{"patient_id": 601,
                             "attending_username": 'Therien.A',
                             "patient_age": 21,
                             "heart_rate": [70, 65],
                             "timestamp": ['2020-03-09 11:00:36',
                                           '2020-03-10 11:00:36'],
                             "status": "not tachycardic"},
                            {"patient_id": 602,
                             "attending_username": 'Duncan.C',
                             "patient_age": 21,
                             "heart_rate": [60, 150],
                             "timestamp": ['2020-03-09 11:00:36',
                                           '2020-03-10 11:02:36'],
                             "status": "tachycardic"},
                            {"patient_id": 603,
                             "attending_username": 'Bob.D',
                             "patient_age": 40,
                             "heart_rate": [90, 80],
                             "timestamp": ['2020-03-09 11:00:36',
                                           '2020-03-10 11:01:36'],
                             "status": "not tachycardic"},
                            {"patient_id": 604,
                             "attending_username": 'Williamson.Z',
                             "patient_age": 19,
                             "heart_rate": [70, 105],
                             "timestamp": ['2020-03-09 11:00:36',
                                           '2020-03-10 11:00:36'],
                             "status": "tachycardic"}],
                           [{"last_heart_rate": 150,
                             "last_time": "2020-03-10 11:02:36",
                             "patient_id": 602,
                             "status": "tachycardic"},
                            {"last_heart_rate": 80,
                             "last_time": "2020-03-10 11:01:36",
                             "patient_id": 603,
                             "status": "not tachycardic"}]),
                          ([], [], [])])
def test_patients_for_attending_username(patient_id_list, pat_db, expected):
    from heart_rate_server import patient_db, patients_for_attending_username
    for patient in pat_db:
        patient_db.append(patient)
    answer = patients_for_attending_username(patient_id_list)
    assert answer == expected
