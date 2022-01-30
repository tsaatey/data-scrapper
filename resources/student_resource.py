from utils.response import APIResponse
import requests
import pandas as pd


class StudentResource:
    def __init__(self, payload = None):
        self.payload = payload
        self.origin = f"https://{payload['school_url']}"
        self.referer = f"https://{payload['school_url']}/"

    def login(self):
        payload = {
            "username": self.payload['username'],
            "password": self.payload['password'],
            "grant_type": "password"
        }
        url = "https://apivm.unilynq.com/token"
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.origin,
            "Referer": self.referer
        }

        response = requests.post(url = url, data = payload, headers = headers)
        if response.status_code == 400:
            # Bad request
            return APIResponse(False, response.json()['error_description'])

        access_token = response.json()['access_token']
        return APIResponse(True, 'success', access_token)

    def get_students(self):
        _response = self.login()

        # If login is not successful, abort
        if not _response.status:
            return _response

        # Login is successful
        # Get all programmes of the school
        _res = self.get_school_programs(_response.data)
        programs = _res.data

        # Retrieve batch from submitted data
        batch = self.payload['batch']

        # Url to get students data
        url = "https://apivm.unilynq.com/api/students/v2/cssps"

        # Set header parameters
        headers = {
            "Authorization": f"Bearer {_response.data}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        student_ids = []
        student_names = []
        student_genders = []
        student_dobs = []
        student_programmes = []

        # Iterate over the programmes and get all students for each
        for program in programs:
            payload = {
                "batch": batch,
                "program": program['DeptName']
            }

            response = requests.post(url, json = payload, headers = headers)
            students = response.json()['CSSPS']

            if students:
                for student in students:
                    student_names.append(student['student_name'])
                    student_genders.append(student['gender'])
                    student_dobs.append(student['dob'])
                    student_programmes.append(student['program'])

        file = pd.DataFrame({"Candidate name": student_names, "Gender": student_genders, "Date of Birth": student_dobs, "Programme": student_programmes})
        # Create the excel template
        writer = pd.ExcelWriter("student_data.xlsx")
        file.to_excel(writer, sheet_name = "Sheet1", startrow=0, index=True, index_label = "SN")
        writer.save()

        return APIResponse(True, 'Students data successfully extracted to excel')

    def get_school_programs(self, token):
        url = "https://apivm.unilynq.com/api/programs/v2/all"
        headers = {
            "Authorization": f"Bearer {token}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        response = requests.get(url = url, headers = headers)
        programs = response.json()

        return APIResponse(True, 'success', programs)

