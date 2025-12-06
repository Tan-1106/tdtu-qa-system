from enum import Enum
from dataclasses import dataclass


@dataclass(frozen=True)
class FacultyInfo:
    first_char: str
    name: str
    

class Faculty(Enum):
    A = FacultyInfo("0", "Khoa Ngoại Ngữ")
    B = FacultyInfo("1", "Khoa Mỹ Thuật Công Nghiệp")
    C = FacultyInfo("2", "Khoa Kế Toán")
    D = FacultyInfo("3", "Khoa KHXH & Nhân Văn")
    E = FacultyInfo("4", "Khoa Điện - Điện Tử")
    F = FacultyInfo("5", "Khoa Công Nghệ Thông Tin")
    G = FacultyInfo("6", "Khoa Khoa Học Ứng Dụng")
    H = FacultyInfo("7", "Khoa Quản Trị Kinh Doanh")
    I = FacultyInfo("8", "Khoa Kỹ Thuật Công Trình")
    J = FacultyInfo("9", "Khoa Môi Trường & BHLĐ")
    K = FacultyInfo("A", "Khoa Lao Động Công Đoàn")
    L = FacultyInfo("B", "Khoa Tài Chính Ngân Hàng")
    M = FacultyInfo("C", "Khoa Toán - Thống Kê")
    N = FacultyInfo("D", "Khoa Khoa Học Thể Thao")
    O = FacultyInfo("E", "Khoa Luật")
    P = FacultyInfo("H", "Khoa Dược")
    
    
    
class Role(Enum):
    ADMIN = "Admin"
    FACULTY_MANAGER = "Faculty Manager"
    TEACHER = "Teacher"
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