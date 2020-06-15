import pytest
import numpy as np


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
                          ({"patient_id": "abc",
                            "attending_username": "Canyon.D",
                            "patient_age": 20}, "ERROR"),
                          ({"patient_id": 5,
                            "attending_username": "Canyon.D",
                            "patient_age": "a20"}, "ERROR")])
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
