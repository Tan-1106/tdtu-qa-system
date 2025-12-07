from enum import Enum
from dataclasses import dataclass
    
class Role(Enum):
    ADMIN = "Admin"
    TEACHER = "Teacher"
    STUDENT = "Student"

'''
{
    'provider': 'ELIT Auth',
    'uid': '111083632316595044145',
    'sub': '52200081',
    'username': 'S52200081',
    'nickname': 'Nguyễn Nhật Tân',
    'name': 'Nguyễn Nhật Tân',
    'email': '52200081@student.tdtu.edu.vn',
    'image': 'https://lh3.googleusercontent.com/a/ACg8ocKPbiWhOLTfHRPn55i5ZkDVQgMtgVI9clBP1rbBwnWmfe4osA=s96-c',
    'email_verified': True,
    'given_name': 'Tân', 
    'family_name': 'Nguyễn Nhật',
    'info': {
        'image': 'https://lh3.googleusercontent.com/a/ACg8ocKPbiWhOLTfHRPn55i5ZkDVQgMtgVI9clBP1rbBwnWmfe4osA=s96-c'
    },
    'extra': {
        'raw_info': {
            'image': 'https://lh3.googleusercontent.com/a/ACg8ocKPbiWhOLTfHRPn55i5ZkDVQgMtgVI9clBP1rbBwnWmfe4osA=s96-c'
        }
    },
    'is_admin': False,
    'is_teacher': False,
    'is_student': True,
    'faculty': 'Khoa Công Nghệ Thông Tin',
    'faculty_code': '5',
    'is_faculty_manager': False,
    'access_token': 'e9db6b739a0cf90a3e118d34ecabab655f4108ba',
    'refresh_token': '1d20df1a-cbd9-4045-a5dd-da4b1abfc839'
}
'''