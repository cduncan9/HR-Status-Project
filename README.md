# heart-rate-sentinel-server-duncan-therien
heart-rate-sentinel-server-duncan-therien created by GitHub Classroom

The Heart Rate Sentinel Projects is comprised of three python files: heart_rate_server.py, heart_rate_client.py,
and test_heart_rate_server.py. The heart_rate_server.py runs a server using Flask and has routes following the 
specifications on the GitHub assignment page. These routes include "POST /api/new_patient" (adds a patient to database), "POST /api/new_attending" (adds a new attending physician to database), "POST /api/heart_rate" (logs a heart rate data point to a specified patient and emails physician if heart rate is tachycardic), "GET /api/status/<patient_id>" (returns patient status), "GET /api/heart_rate/<patient_id>" (returns list of previous heart rate measurements), "GET /api/heart_rate/average/<patient_id>" (returns list of patients heart rate readings), "POST /api/heart_rate/interval_average" (returns average heart rate after input timestamp), and "GET /api/patients/<attending_username>" (returns all patient info assigned to given attendant). A more in depth description of route functionality may be found on the GitHub assignment page. The file heart_rate_client.py is a python file that interacts with the server to demonstrate the server's functionality. The file test_hear_rate_server.py contains all the unit testing for helper methods contained in heart_rate_server.py.


# Git Status Badge

[![Build Status](https://travis-ci.com/BME547-Summer2020/ecg-analysis-aidan-therien.svg?token=6j6N9bHqFuR9ZZmizj44&branch=master)](https://travis-ci.com/BME547-Summer2020/ecg-analysis-aidan-therien)

# Software License

MIT License

Copyright (c) [2020] [Aidan Therien, Canyon Duncan]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.