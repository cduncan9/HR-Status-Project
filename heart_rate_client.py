import requests

server_name = "http://127.0.0.1:5000"

def add_new_patient():
    new_patient = {"patient_id": 100, "attending_username": "Duncan.C", "patient_age": 21}
    r = requests.post(server_name+"/api/new_patient", json=new_patient)
    print(r.text)


if __name__ == '__main__':
    add_new_patient()