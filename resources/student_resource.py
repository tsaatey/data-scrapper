from utils.response import APIResponse
import os
import requests
import pandas as pd


class StudentResource:
    def __init__(self, payload=None):
        self.payload = payload
        self.origin = f"https://{payload['school_url']}"
        self.referer = f"https://{payload['school_url']}/"

    def login(self):
        payload = {
            "username": self.payload['username'],
            "password": self.payload['password'],
            "grant_type": "password"
        }
        headers = {
            "Content-Type": "application/x-www-form-urlencoded",
            "Origin": self.origin,
            "Referer": self.referer
        }

        response = requests.post(url=os.environ.get('LOGIN_URL'), data=payload, headers=headers)
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

        # Set header parameters
        headers = {
            "Authorization": f"Bearer {_response.data}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        student_ids = []
        student_last_names = []
        student_first_names = []
        student_middle_names = []
        student_residency = []
        student_genders = []
        student_dobs = []
        student_programmes = []
        student_parent_phones = []

        # Iterate over the programmes and get all students for each
        for program in programs:
            payload = {
                "batch": batch,
                "program": program['DeptName']
            }

            response = requests.post(url=os.environ.get("STUDENT_LIST_URL"), json=payload, headers=headers)
            students = response.json()['CSSPS']

            if students:
                for student in students:
                    # Split the student name to get first name, last name, and middle name
                    name = student['student_name'].title()
                    name_list = name.split(" ")

                    # Only Last name and First name
                    if len(name_list) == 2:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append("")

                    # Has last name, first name, and middle name
                    if len(name_list) == 3:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append(name_list[2])

                    # Has last name, first name, more than one middle name
                    if len(name_list) > 3:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append(name_list[2] + " " + name_list[3])

                    gender = "Male" if student['gender'] == "M" else "Female"
                    student_genders.append(gender)
                    student_dobs.append(student['dob'])

                    if student['program'].title() == "General Science":
                        program = "General Programme in Science"
                    elif student['program'].title() == "Business":
                        program = "Business(Accounting)"
                    elif student['program'].title() == "General Arts":
                        program = "General Programme in Arts"
                    else:
                        program = student['program'].title()

                    student_programmes.append(program)
                    student_parent_phones.append(student['phone'])
                    student_residency.append(student['residential_status'].title())

        file = pd.DataFrame(
            {"First Name": student_first_names, "Middle Name": student_middle_names, "Last Name": student_last_names,
             "Gender": student_genders, "Date of Birth": student_dobs,
             "Programme": student_programmes, "Residency": student_residency})

        # Create the Excel template
        writer = pd.ExcelWriter(f"{self.payload.filename}.xlsx")
        file.to_excel(writer, sheet_name="Sheet1", startrow=0, index=True, index_label="SN")
        writer.close()

        return APIResponse(True, 'Students data successfully extracted to excel')

    def get_school_programs(self, token):
        headers = {
            "Authorization": f"Bearer {token}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        response = requests.get(url=os.environ.get("PROGRAM_LIST_URL"), headers=headers)
        programs = response.json()

        return APIResponse(True, 'success', programs)

    def change_student_program(self):
        pass

    def get_student_as_electorates(self):
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

        # Set header parameters
        headers = {
            "Authorization": f"Bearer {_response.data}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        student_ids = []
        student_last_names = []
        student_first_names = []
        student_middle_names = []
        student_genders = []

        # Iterate over the programmes and get all students for each
        for program in programs:
            payload = {
                "batch": batch,
                "program": program['DeptName']
            }

            response = requests.post(url=os.environ.get("STUDENT_LIST_URL"), json=payload, headers=headers)
            students = response.json()['CSSPS']

            if students:
                for student in students:
                    # Split the student name to get first name, last name, and middle name
                    name = student['student_name'].upper()
                    name_list = name.split(" ")

                    # Only Last name and First name
                    if len(name_list) == 2:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append("")

                    # Has last name, first name, and middle name
                    if len(name_list) == 3:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append(name_list[2])

                    # Has last name, first name, more than one middle name
                    if len(name_list) > 3:
                        student_last_names.append(name_list[0])
                        student_first_names.append(name_list[1])
                        student_middle_names.append(name_list[2] + " " + name_list[3])

                    student_genders.append(student['gender'])
                    student_ids.append(student['jhs_number'])

        file = pd.DataFrame(
            {"studentid": student_ids, "firstname": student_first_names, "lastname": student_last_names,
             "othernames": student_middle_names,
             "gender": student_genders})

        # Create the Excel template
        writer = pd.ExcelWriter(f"{self.payload['filename']}.xlsx")
        file.to_excel(writer, sheet_name="Sheet1", startrow=0, index=True, index_label="SN")
        writer.close()

        return APIResponse(True, 'Students data successfully extracted to excel')

    def get_student_with_parent_contacts(self):
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

        # Set header parameters
        headers = {
            "Authorization": f"Bearer {_response.data}",
            "Origin": self.origin,
            "Referer": self.referer
        }

        student_ids = []
        student_genders = []
        student_parent_names = []
        student_parent_phones = []
        student_classes = []
        student_residencies = []
        student_names = []

        programmes = {"ARTS": [1, 2, 3, 4, 5, 6, 7, 8, 9], "BUSINESS": [1, 2], "SCIENCE": [1, 2, 3, 4],
                      "HOME%20ECONS": [1, 2, 3, 4], "V.%20ARTS": [1, 2, 3], "AGRIC": [1]}

        # Iterate over the programmes and get all students for each
        for program, classes in programmes.items():
            for _class in classes:
                response = requests.get(f'https://apivm.unilynq.com/api/students/v2/all/{program}%20{_class}/2/120/1',
                                        headers=headers)
                students = response.json()['students']

                if students:
                    for student in students:
                        student_names.append(
                            student['LynQLstname'] + " " + student['LynQFstname'] + " " + student['LynQOnames'])
                        student_genders.append(student['LynQGender'])
                        student_ids.append(student['Short'])
                        student_parent_phones.append(student['pg_mobile_main'] if student['pg_mobile_main'] else "")
                        guardian = student['pg_name']
                        if guardian:
                            student_parent_names.append(guardian[3:])
                        else:
                            student_parent_names.append("")
                        student_classes.append(student['LynQProg'])
                        student_residencies.append(student['LynQTivity'])

        file = pd.DataFrame(
            {"INDEX NUMBER": student_ids, "STUDENT NAME": student_names, "SEX": student_genders,
             "CLASS": student_classes, "RESIDENCY": student_residencies,
             "GUARDIAN": student_parent_names, "GUARDIAN PHONE": student_parent_phones})

        # Create the Excel template
        writer = pd.ExcelWriter(f"{self.payload['filename']}.xlsx")
        file.to_excel(writer, sheet_name="Sheet1", startrow=0, index=True, index_label="SN")
        writer.close()

        return APIResponse(True, 'Students data successfully extracted to excel')
