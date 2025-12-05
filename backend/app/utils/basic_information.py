from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class FacultyInfo:
    first_char: str
    name: str
    

class Faculty(Enum):
    FFL = FacultyInfo("0", "Khoa Ngoại Ngữ")
    IFA = FacultyInfo("1", "Khoa Mỹ Thuật Công Nghiệp")
    AAF = FacultyInfo("2", "Khoa Kế Toán")
    SSH = FacultyInfo("3", "Khoa KHXH & Nhân Văn")
    FEEE = FacultyInfo("4", "Khoa Điện - Điện Tử")
    IT = FacultyInfo("5", "Khoa Công Nghệ Thông Tin")
    FAS = FacultyInfo("6", "Khoa Khoa Học Ứng Dụng")
    FBA = FacultyInfo("7", "Khoa Quản Trị Kinh Doanh")
    CIVIL = FacultyInfo("8", "Khoa Kỹ Thuật Công Trình")
    ENLABSAFE = FacultyInfo("9", "Khoa Môi Trường & BHLĐ")
    LRTU = FacultyInfo("A", "Khoa Lao Động Công Đoàn")
    FINANCE = FacultyInfo("B", "Khoa Tài Chính Ngân Hàng")
    FMS = FacultyInfo("C", "Khoa Toán - Thống Kê")
    FSS = FacultyInfo("D", "Khoa Khoa Học Thể Thao")
    LAW = FacultyInfo("E", "Khoa Luật")
    FOP = FacultyInfo("H", "Khoa Dược")
    
    
    
class Role(Enum):
    ADMIN = "Admin"
    FACULTY_MANAGER = "Faculty Manager"
    STUDENT = "Student"


def get_user_info(user_sub: str):
    first_char = user_sub[0].upper()
    for faculty in Faculty:
        if faculty.value.first_char == first_char and len(user_sub) == 8:
            return {
                "faculty": faculty.value.name,
                "role": Role.STUDENT.value
            }
    return {
        "role": None,
        "faculty": None
    }