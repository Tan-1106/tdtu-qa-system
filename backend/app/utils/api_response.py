def success_response(data=None, message="Success", status_code=200):
    return {
        "status": "success",
        "message": message,
        "data": data
    }, status_code


def error_response(message="Error", code=400, details=None):
    return {
        "status": "error",
        "message": message,
        "error": {
            "code": code,
            "details": details
        }
    }, code
