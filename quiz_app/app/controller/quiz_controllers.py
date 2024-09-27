
from typing import Annotated

from fastapi import Depends, HTTPException
from sqlalchemy import func
from sqlmodel import Session, select
from app.db.db_connector import get_session
from app.model.quiz_models import Catagory, CategoryMarks, CategoryQuizDetails, Choices, CreateCatagory,Quiz, QuizAttemptModel
from app.model.user_models import User


def insert_catagory(catagory_form:CreateCatagory, session:Annotated[Session, Depends(get_session)]):
    if catagory_form:
        # varify catagory is exist
        db_catagory=session.exec(select(Catagory).where(Catagory.catagory_name==catagory_form.catagory_name)).first()
        if db_catagory and db_catagory.catagory_name==catagory_form.catagory_name:
            raise HTTPException(status_code=404, detail="Catagory is already exist")
        
        try:
            catagory= Catagory(catagory_name=catagory_form.catagory_name, catagory_description=catagory_form.catagory_description)
            print("I am in try block")
            session.add(catagory)
            session.commit()
            session.refresh(catagory)
            return catagory
        except:
           raise HTTPException(status_code=404, detail="catagory is not be added")
            
        
    else:
        raise HTTPException(status_code=404, detail="catagory_form not found")
    
    
# def insert_quiz_level(quiz_level_data:CreatQuizLevel, session:Annotated[Session, Depends(get_session)]):
#     if not quiz_level_data:
#         raise HTTPException(status_code=404, detail="Quiz lavel data is missing")
    
#     # varify the catagory id of quize_levl_data is exist in databasse
    
#     db_catagory= session.get(Catagory, quiz_level_data.catagory_id)
    
#     if not db_catagory:
#         raise HTTPException(status_code=404, detail="catagory is not exist in database")
    
#     existing_quiz_level_data=session.exec(select(QuizLevel).where(QuizLevel.catagory_id==quiz_level_data.catagory_id))
    
#     if existing_quiz_level_data:
        
#         # varyfy quiz_level is exist 
#         for existing_quiz in existing_quiz_level_data:
#             if existing_quiz.quiz_level==quiz_level_data.quiz_level:
#                 raise HTTPException(status_code=404, detail="Quiz leval is already exist")
     
#     new_quiz_data=QuizLevel(quiz_level=quiz_level_data.quiz_level,catagory_id=quiz_level_data.catagory_id)
    
#     session.add(new_quiz_data)
#     session.commit()
#     session.refresh(new_quiz_data)
#     new_quiz_data=QuizLevel(quiz_level=quiz_level_data.quiz_level,catagory_id=quiz_level_data.catagory_id)
    
#     return new_quiz_data

# def get_choices(question_id: int | None, session: Session):
#     statment = select(Choices).where(question_id == Choices.quiz_id)
#     choices = session.exec(statment).all()
#     return choices

def get_quiz(user_id:int, catagory_name:str, session:Annotated[Session, Depends(get_session)]):
    
  # we can do by follows 
    """ 
    # get no of remaining_questions
    attempted_quiz_detail= session.exec(select(CategoryQuizDetails).where(CategoryQuizDetails.user_id==user_id)).first()
    if attempted_quiz_detail is not None:
        remaining_questions= attempted_quiz_detail.remaining_questions
        
    # get catagory_id 
    catagory_detail=session.exec(select(Catagory).where(Catagory.catagory_name==catagory_name)).first()
    if catagory_detail is not None:
        catagory_id= catagory_detail.catagory_id
    
    """
   #get the remaining_questions and catagory_id of spacific catagory from CategoryQuizDetails tables
   
    attempted_quiz_detail=session.exec((select(CategoryQuizDetails).join(Catagory)
                                 .where(CategoryQuizDetails.user_id==user_id)
                                 .where(Catagory.catagory_name==catagory_name))).one()
    
    catagory_id= attempted_quiz_detail.category_id
    remaining_questions= attempted_quiz_detail.remaining_questions
 
    # get random questions with remaining question limited
    questions = session.exec(select(Quiz).where(Quiz.catagory_id == catagory_id).order_by(func.random()).limit(remaining_questions)).all()
    
    choices=[]
    
    for question in questions:
        choice= question.questions # here questions attributes have choices value
        choices.append(choice)

    return {
        "remaining_question":remaining_questions,
        "questions": questions,
        "choices":choices
        
    }

    
    
def isQuizAvailble(catagory_name:str, session:Annotated[Session, Depends(get_session)]):
    
    # get the all the question for spacific catagory 
    quiz=session.exec((select(Quiz).join(Catagory).where(Catagory.catagory_name==catagory_name))).all()
    
    if len(quiz)>9:
        return True
    else:
        return False
    
   
def getAttemptedQuizdetail(user_id:int, catagory_name:str, session:Annotated[Session, Depends(get_session)]):
    
    # varify catagory is exist
    catagory=session.exec(select(Catagory).where(Catagory.catagory_name==catagory_name)).first()
    if not catagory:
        raise HTTPException(status_code=404, detail=f'{catagory_name} is not available')
    
    # varyfi quiz is available
    # isAvailable=isQuizAvailble(catagory_name=catagory_name, session=session)
    # if not isAvailable:
    #     raise HTTPException(status_code=404, detail=f'Quiz is not available for {catagory_name} catgory')
    
    
    # retrive attempted_quiz_ detailss
    
    attempted_quiz_detail=session.exec((select(CategoryQuizDetails,CategoryMarks) # without relationship
                  .where(CategoryMarks.category_id==catagory.catagory_id)
                  .where(CategoryQuizDetails.user_id==user_id)
                  .where(CategoryQuizDetails.category_id==catagory.catagory_id)))
    
    # catagory_detail return dictiory with commbination of CategoryQuizDetails and CategoryMarks
     # getting catagoryDetail and catagorymarks from catagory_detail dictionary
    for catagoryDetail, catagorymarks in attempted_quiz_detail:
        if catagoryDetail:
            print(catagoryDetail)
            detail= catagoryDetail.model_dump()
            # check if user attempt then show the detail
            if catagoryDetail.remaining_questions < 10:
                detail.update({
                    "catagory_marks":catagorymarks.marks
                })
                return {
                    "isAttempt": True,
                    "quizDetail": detail
                }
            return {
                "isAttempt":False,
                "quizDetail":f"You have never attempted {catagory.catagory_name} questions"
            }    
                
            
    # add catagory details for the user if it is not present
    caragory_detail_table= CategoryQuizDetails(user_id=user_id,category_id=catagory.catagory_id, obtaining_marks=0) 
    session.add(caragory_detail_table) 
    session.commit()
    return {
                "isAttempt":False,
                "quizDetail":f"You have never attempted {catagory.catagory_name} questions"
            }  
    
    


def attempt_quiz(attempt_form:QuizAttemptModel, session:Annotated[Session, Depends(get_session)]):
    if not attempt_form:
        raise HTTPException(status_code=404, detail="form data is missing")
    
    """ 
    1: varify attempt_quiz_of spacific user is already exist in CategoryQuizDetails
    
    if exist:
          varify its is finished or not:
          if not finished
                    update the the CategoryQuizDetails of obtaining_marks,remaining_questions and percentage
          else finished: 
                    return " you can not attempt the the quize because it is finished"
                    
    elase Not exist: 
                add the attempt_form data into CategoryQuizDetails table
               
    """
    
    
    
    # 1 varify user have take quiz already
    catagory_detail=session.exec((select(CategoryQuizDetails,CategoryMarks)
                   .where(Catagory.catagory_id==attempt_form.category_id)
                   .where(CategoryQuizDetails.category_id==attempt_form.category_id)
                   .where(CategoryQuizDetails.user_id==attempt_form.user_id)))
    
    for catagoryDetail, catagoryMrks in catagory_detail:
        if catagoryDetail:
            # check quiz is already finished or nor
            if not catagoryDetail.is_finished:
                # update the quiz detail for the user
                catagoryDetail.obtaining_marks+= attempt_form.obtaining_marks
                catagoryDetail.remaining_questions -= 1
                catagoryDetail.percentage= int ( (catagoryDetail.obtaining_marks/catagoryMrks.marks) * 100)
                
                if attempt_form.isFinished:
                    catagoryDetail.is_finished=True
                    # determine the ranke based on obtaining marks
                    if catagoryDetail.obtaining_marks< 20:
                        catagoryDetail.rank= "poor"
                    elif catagoryDetail.obtaining_marks < 30:
                        catagoryDetail.rank= "Better"
                    elif catagoryDetail.obtaining_marks < 40:
                        catagoryDetail.rank= "Good"
                    else:
                        catagoryDetail.rank = "Excelent"
                    session.commit()
                    session.refresh(catagoryDetail)
                    return f"You have attempted {attempt_form.category_id} category quiz"
                
                session.commit()
                return f"Your Quiz details for {attempt_form.category_id} category has been updated successfully"        
       
        return f"You can't attempt {attempt_form.category_id} category quiz, because you have already attempted"
                          
    else:
        # if it is firstime
        quiz_details_table=CategoryQuizDetails(category_id=attempt_form.category_id, obtaining_marks=attempt_form.obtaining_marks,user_id=attempt_form.user_id,is_finished=attempt_form.isFinished)
        session.add(quiz_details_table)
        session.commit()
        session.refresh(quiz_details_table)
    return quiz_details_table




       
def getAllQuiz(user_id:int, session:Annotated[Session, Depends(get_session)]):
    
    # todo
    details:list = []
    all_catagory_marks=0
    
    # get all catagories
    catagories=session.exec(select(Catagory)) 
    
    # check catagory one by one
    for catagory in catagories:
        # get attempted_quiz from each catagory
        attempted_quiz= session.exec(select(CategoryQuizDetails)
                                      .where(CategoryQuizDetails.user_id== user_id)
                                      .where(CategoryQuizDetails.category_id==catagory.catagory_id)).first()
        if attempted_quiz:
            return attempt_quiz
        
        
        
        
        
        




       
def deleteQuiz(user_id:int, catagory_id:int, session:Annotated[Session, Depends(get_session)]):
    
    
    # Query to fetch the category quiz details and user
    attempteed_quiz_detail=session.exec(select(CategoryQuizDetails,User)
                 .where(User.user_id==user_id)
                 .where(CategoryQuizDetails.user_id==user_id)
                 .where(CategoryQuizDetails.category_id==catagory_id)).first()
    
    
    # check if the query  returned any results
    if not attempteed_quiz_detail:
        raise HTTPException(status_code=404, detail="user or quiz are not found")
    
    # Destructure the result into catagoryDetail, user to perform further operation
    catagoryDetail , user  = attempteed_quiz_detail
    
     
    # Perform deletion if both categoryDetail and user exist
    if catagoryDetail and user:
            session.delete(catagoryDetail)
            session.commit()
            return f'Quiz has been deleted'
    
    
    # If no valid category or user, raise an exception
    raise HTTPException(status_code=404, detail="User or category does not exist")