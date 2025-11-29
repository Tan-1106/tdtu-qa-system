from langdetect import detect

from app.services import question_service, model_service

# # Lấy tất cả câu hỏi
# async def get_questions():
#     questions = await question_service.get_questions()
#     return questions


# # Lấy câu hỏi theo ID
# async def get_question_by_id(question_id: str):
#     question = await question_service.get_question_by_id(question_id)
#     return question


# # Đặt câu hỏi
# async def query(question_data: dict, user_id: str):
#     question_data['user_id'] = user_id
#     lang = detect(question_data['question'])
    
#     # Tạo câu hỏi
#     question = await question_service.create_question(question_data)
#     try:
#         # Lấy câu trả lời
#         if lang == 'vi':
#             answer = await question_service.query(question_data)
#         else:
#             question_data['translated_question'] = await model_service.translate_to_vietnamese(question_data['question'])
#             answer = await question_service.query(question_data, lang='en')
        
#         # Cập nhật trạng thái câu hỏi với câu trả lời
#         result = await question_service.update_question_status(question.id, answer)

#     except Exception as e:
#         await question_service.update_question_status(question.id, f"Error: Cannot get answer. {str(e)}", status="Failed")
#         raise e

#     return result


# # Để lại phản hồi cho câu hỏi
# async def leave_feedback(question_id: str, user_id: str, feedback: str):
#     question = await question_service.leave_feedback(question_id, user_id, feedback)
#     return question