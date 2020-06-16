import requests

server_name = "http://127.0.0.1:5000"


def add_new_patient():
    new_patient = {"patient_id": 1,
                   "attending_username": "Duncan.C",
                   "patient_age": 21}
    r = requests.post(server_name+"/api/new_patient", json=new_patient)
    print(r.text)
    new_patient = {"patient_id": 2,
                   "attending_username": "Therien.A",
                   "patient_age": 21}
    r = requests.post(server_name + "/api/new_patient", json=new_patient)
    print(r.text)
    new_patient = {"patient_id": 3,
                   "attending_username": "Therien.A",
                   "patient_age": 65}
    r = requests.post(server_name + "/api/new_patient", json=new_patient)
    print(r.text)


def add_heart_rate():
    new_heart_rate = {"patient_id": 3, "heart_rate": 200}
    r = requests.post(server_name+"/api/heart_rate", json=new_heart_rate)
    print(r.text)


def add_new_attendant():
    new_attendant = {"attending_username": "Duncan.C",
                     "attending_email": "c.duncan@duke.edu",
                     "attending_phone": "919-265-9874",
                     "patients": list()}
    r = requests.post(server_name+"/api/new_attending", json=new_attendant)
    print(r.text)
    new_attendant = {"attending_username": "Therien.A",
                     "attending_email": "a.therien@duke.edu",
                     "attending_phone": "919-265-9874",
                     "patients": list()}
    r = requests.post(server_name + "/api/new_attending", json=new_attendant)
    print(r.text)


def get_heart_rate():
    r = requests.get(server_name+"/api/status/1")
    print(r.text)

if __name__ == '__main__':
    add_new_attendant()
    add_new_patient()
    add_heart_rate()
    get_heart_rate()
