from fastapi import FastAPI,Depends, HTTPException, Request, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
import uvicorn
from contextlib import asynccontextmanager
from typing import Annotated
from app.controller.admin_controller import AdminsignUpFn, adminLoginFn, insert_question, insrt_catagory_marks
from app.controller.auth_controller import generateDecodedToken, generateToken, passwordIntoHash
from app.controller.quiz_controllers import attempt_quiz, deleteQuiz, get_quiz, getAllQuiz, getAttemptedQuizdetail, insert_catagory,isQuizAvailble
from app.db.db_connector import create_table, get_session
from app.model.user_models import User, Token
from app.model.admin_models import Admin, AdminLogin, AdminSignup, AdminToken
from app.model.quiz_models import Catagory, CategoryMarks, CategoryQuizDetails, Create_Quiz, Quiz, Choices, QuizAttemptModel
from app.utils.exceptions import ConflictException, InvalidInputException, NotFoundException
from app.controller.user_controllers import  loginFn, signupFn, tokenService
from datetime import datetime, timedelta
from app.setting import access_expiry_time

auth_schema = OAuth2PasswordBearer(tokenUrl="/token")

@asynccontextmanager
async def lifespan(app=FastAPI):
    print("tabel is creating...")
    create_table()
    print("tabel is created")
    yield
    


app: FastAPI= FastAPI(lifespan=lifespan, title="Quiz app", version="1.0.0")


# add middleware after app object
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["*"]
)

@app.get("/")
async def route():
    return "Welcome to our Quiz App Project"

#-----------/////////////----------------------exception_handling--------------//////////////////-----------------------------------

@app.exception_handler(NotFoundException)
def not_found(request:Request, exception:NotFoundException):
    return JSONResponse(status_code=404,content=f"{exception.not_found} not found")


@app.exception_handler(ConflictException)
def exist_input(request:Request, exception:ConflictException):
    return JSONResponse(status_code=404, content=f"This {exception.conflict_input}  already exist")

@app.exception_handler(InvalidInputException)
def invalid_input_error(request:Request, exception:InvalidInputException):
    return JSONResponse(status_code=404, content=f'{exception.invalid_input} is invalid')


#-----------/////////////----------------------User Routing-------------//////////////////-----------------------------------



    
# signUp route

"""
Main logic:
1: user will submit formData have userName, userEnail and userPaswword
2: verify that the user credential is exist or not
     if exist then raise the exception
     otherwise 
        (a):save the user credential in database
          for this first convert the userPassword int hash_password and then add into database
        (b): Generate access and refresh tokens for the new user
           add the refresh_token into database for generate the access_token when needed

3:add the "access_token" with "access_expiry_time" and "refresh_token" with "refresh_expiry_time" in cookies.

Note: Here to complete the 2nd process we depends upon signupFn that return Token_data having     
          {
        "access_token": {
            "token": access_token,
            "access_expiry_time": access_expiry_time
        },
        "refresh_token": {
            "token": refresh_token,
            "refresh_expiry_time": refresh_expiry_time
        }
    }


"""
@app.post("/api/userSignup")
def userSignup(response:Response, token_data:Annotated[dict,Depends(signupFn)]):
    # return token_data
    
    if token_data:
        print(token_data["refresh_token"]
              ["refresh_expiry_time"].total_seconds())
        response.set_cookie(key="access_token",
                            value=token_data["access_token"]["token"],
                            expires=int(
                                token_data["access_token"]["access_expiry_time"].total_seconds())
                            )
        response.set_cookie(key="refresh_token",
                            value=token_data["refresh_token"]["token"],
                            max_age=int(
                                token_data["refresh_token"]["refresh_expiry_time"].total_seconds())
                            )

        return "You have registered successfully"
    raise NotFoundException("User")
    


# sign In route
@app.post("/api/signin")
async def signIn(token_data:Annotated[dict, Depends(loginFn)]):
    return token_data



# Get Data With Token
@app.get("/api/get_data_with_token")
def get_data_with_token(token:str, session:Annotated[Session,Depends(get_session)]):
    
    if token:
        decodeded_token=generateDecodedToken(token)
        # return decodeded_token
        user_email= decodeded_token["user_email"]
        # return user_email
        
        user_data=session.exec(select(User).where(User.user_email==user_email)).first()
        
        if user_data:
            # we do not want send the user_paswort to our client
            return {
                    "user_email":user_data.user_email ,
                    "user_name": user_data.user_name,
                    "user_id": user_data.user_id
                    }
        else:
            raise HTTPException(status_code=404, detail="uaser not found")
        
    else:
        raise HTTPException(status_code=404, detail="token is not provided")



# sign Out user
@app.delete("/api/user_sign_out")
def user_sign_out(token:str, session:Annotated[Session, Depends(get_session)]):
    
    if token:
        decoded_data= generateDecodedToken(token)
        user_email= decoded_data["user_email"]
        # get user
        user_data =session.exec(select(User).where(User.user_email==user_email)).first()
        
        """ 
        To delete the user you have need to delete the user token
        bcz  usr_id is also store in Token table as forign_key
        """
       
        # get user_d from user_data to acess the Token 
        if user_data is not None:  # error handling becz it may be None
            user_id= user_data.user_id
     
        else:
            raise HTTPException(status_code=404, detail="User id is None")
        
        tokens=session.exec(select(Token).where(Token.user_id==user_id)).all()
        
       
        
        if tokens:
            print("tokin is exist")

            for db_token in tokens:
                session.delete(db_token)
            session.commit()
            
            print("token deleted now preseeding to delete the user")
            
            session.delete(user_data)
            session.commit()
            return "User seccesfully logout"
        else:
            raise HTTPException(status_code=404, detail="Tokens is invalid")
    else:
        raise HTTPException(status_code=404, detail="Token not provided")


# delete the user
@app.delete("/api/deleteUser")
def delete_user(id:int, session:Annotated[Session, Depends(get_session)]):
    
    """ 
    To delete the user you have need to delete the user token
    bcz  usr_id is also store in Token table as forign_key
    
    """
    
    user=session.get(User, id)
    tokens=session.exec(select(Token).where(Token.user_id==id)).all()
    
    if not user:
        raise HTTPException(status_code=404, detail="user is not exist")
    
        
    if tokens:
        print("tokin is exist")
        
        for token in tokens:
            session.delete(token) # delete 
            
        session.commit() # commitig the deleted tokrn db
        
        print("token deleted now preseeding to delete the user")
        
        session.delete(user)
        session.commit()
        
        return "User and their token succesfully deleted"
       
    else:
        raise HTTPException(status_code=404, detail="token is not exist")
    
    
# refresh Token
@app.get("/api/refresh")
def refresh_token(token:str , session:Annotated[Session, Depends(get_session)]):
    if token:
        decoded_token= generateDecodedToken(token)
        user_email= decoded_token["user_email"]
        
        user_data=session.exec(select(User).where(User.user_email==user_email)).first()
        if user_data is not None:
            db_user_email= user_data.user_email
            db_user_name = user_data.user_name
        else:
            raise HTTPException(status_code=404, detail="User has None value")
        
        data={
           "user_name": db_user_name,
           "user_email": db_user_email
        }
        
        expiry_time= timedelta(minutes=30)
    
        new_access_token=generateToken(data=data, expiry_time=expiry_time)
        return {"new_acces_token": new_access_token}
        
        
    else:
        raise HTTPException(status_code=404, detail="Token is missing")



#forget password
@app.get("/api/forget_password")
def forget_password(email:str, session:Annotated[Session, Depends(get_session)]):
    user=session.exec(select(User).where(User.user_email==email)).first()
    
    if user is not None:
        db_user_name=user.user_name
        db_user_email= user.user_email
        
    else:
        raise HTTPException(status_code=404, detail="yesr is None")
    
    data={
        "user_name":db_user_email,
        "user_email": db_user_email
    }
    
    expiry_time= timedelta(minutes=30)
    new_token=generateToken(data=data, expiry_time=expiry_time)
    return {"new_access_token": new_token}
    
    
#reset password
@app.post("/api/reset_password")
def rest_password(token:str, new_pasword, session:Annotated[Session, Depends(get_session)]):
    if token and new_pasword:
        decoded_token=generateDecodedToken(token)
        if not decoded_token:
            raise HTTPException(status_code=404, detail="token not converted into decoded")
        
        user_email= decoded_token["user_email"]
        if not user_email:
            raise HTTPException(status_code=404, detail="not found user email")
        
        db_user=session.exec(select(User).where(User.user_email==user_email)).first()
        if not db_user:
            raise HTTPException(404, detail="User is not exist")
        
        user_new_hashed_password=passwordIntoHash(new_pasword)
        if not user_new_hashed_password:
            raise HTTPException(404, detail="new password not converted into hash")
        
        # update the user
        db_user.user_password= user_new_hashed_password
        
        # session.add(db_user)
        session.commit()
        session.refresh(db_user)
        return db_user
        
        
    else:
        raise HTTPException(status_code=404, detail="token or password is missing")



# get access token through refresh token afer access_token expir
@app.get("/api/get_accessToken_through_refreshToken")
def get_accessToken(new_acces_token:Annotated[dict, Depends(tokenService)]):
    if new_acces_token:
        expiriration_time= int(access_expiry_time.total_seconds())
        return {
            "access_token": new_acces_token,
            "expire_in": expiriration_time
        }
    else:
        raise HTTPException(status_code=404, detail="new access  token nob gnerated")
        
#====================================Admin Routes================================================================

# signup
@app.post("/api/adminsignup")
def admin_signup(data:Annotated[dict, Depends(AdminsignUpFn)]):
    return data

# signin       
@app.post("/api/adminlogin")
def admin_login(admindata:Annotated[dict, Depends(adminLoginFn)]):
    if admindata:
        return admindata
    else:
        raise HTTPException(status_code=404, detail="Admin not found")
    
   
    
@app.get("/api/getall")
def get_all_admin(session:Annotated[Session, Depends(get_session)]):
    admins=session.exec(select(Admin)).all()
    return admins
    
    
@app.delete("/api/deletetoken")
def delete_admin(token:str, session:Annotated[Session, Depends(get_session)]):
    db_admin_token=session.exec(select(AdminToken).where(AdminToken.admin_token==token)).first()
    
    if db_admin_token:
        session.delete(db_admin_token)
        session.commit()
        return "token has ben sucessfully deleted"
    
    else:
        raise HTTPException(status_code=404, detail="admin token is not exist is not exist")
    
# varify admin
@app.get("/api/verifyadmin")
def varify_admin(token:str, sessin:Annotated[Session, Depends(get_session)]):
    db_admin_token=sessin.exec(select(AdminToken).where(AdminToken.admin_token==token)).first()
    if db_admin_token:
        return "admin is varified"
    else:
        return " admin token is not varified"
      
#---------------------------------------------Quiz app routes--------------------------------------------------

# add catagory
@app.post("/api/add_catagory")
def add_catagory(added_catagory_data:Annotated[dict, Depends(insert_catagory)]):
    if added_catagory_data:
        return added_catagory_data
    else:
        raise HTTPException(status_code=404,detail="catagory is not added to batabase" )
    
    
    
# get all catagories
@app.get("/api/get_all_catgories")
def get_all_catgories(session:Annotated[Session, Depends(get_session)]):
    catagories=session.exec(select(Catagory)).all()
    
    if catagories:
        return catagories
    else:
        raise HTTPException(status_code=404, detail="Catagories are not exist")
    

# update catagory
# @app.put("/api/update_catagory")
# def update_catagory(catatagory_data:update_catagory_data,catagory_id:int, session:Annotated[Session, Depends(get_session)]):
#     if catatagory_data and catagory_id:
#         catagory=session.exec(select(Catagory).where(Catagory.catagory_id==catagory_id)).first()
#         if not catagory:
#             raise HTTPException(status_code=404, detail="catagory is not exist in database")
#         # return catagory
#         new_catagory= Catagory(catagory_name=catatagory_data.catagory_name, catagory_description=catatagory_data.catagory_description)
#         if not new_catagory:
#             raise HTTPException(status_code=404, detail="data is not be updated")
        
#         session.commit()
#         session.refresh(new_catagory)
#         return new_catagory
        
#     else:
#         raise HTTPException(status_code=404, detail="catagory_data or catagory_id is missing")
    
    
# # delete catagory
# @app.delete("/api/delet_catagory")
# def delete_catagory(catagory_id:int, session:Annotated[Session, Depends(get_session)]):
#     if catagory_id:
#         db_catagory=session.exec(select(Catagory).where(Catagory.catagory_id==catagory_id)).first()
        
#         if not db_catagory:
#             raise HTTPException(status_code=404, detail="catagory is not exist in data base")
#         session.delete(db_catagory)
#         session.commit()
#         return "Catagory is deleted successfully"
        
#     else:
#         raise HTTPException(status_code=404, detail="catagory id is missing")


# # create Quiz Level
# @app.post("/api/add_quiz_level")
# def add_quiz_level(added_quiz_level_data:Annotated[dict, Depends(insert_quiz_level)]):
#     if added_quiz_level_data:
#         return added_quiz_level_data
#     else:
#         raise HTTPException(status_code=404, detail="quize lavel data do not add into data base")
    
# # get all quize lavel
# @app.get("/api/get_all_quiz_levels")
# def get_all_quiz_levels(session:Annotated[Session, Depends(get_session)]):
#     all_bg_quizlevel=session.exec(select(QuizLevel)).all()
#     if all_bg_quizlevel:
#         return all_bg_quizlevel
#     else:
#         raise HTTPException(status_code=404, detail="quiz level not found")


# add questions
@app.post("/api/add_question")
def add_question(new_question:Annotated[dict, Depends(insert_question)]):
    if new_question:
        return new_question
    else: 
        raise HTTPException(status_code=404, detail="quesion is not added into table")
    
    
# add marks of catagory
@app.post("/api/add_catagory_marks")
def add_catagory_marks(added_marks:Annotated[dict, Depends(insrt_catagory_marks)]):
    if added_marks:
        return added_marks
    else:
        raise HTTPException(status_code=404, detail="marks does not added to table")


# get quiz for spacific catagory_name and user
@app.get("/api/get_quiz_for_attempt")
async def get_questions_of_quiz_for_attempt(user_id:int,  catagory_name:str, session:Annotated[Session, Depends(get_session)]):
    questions= get_quiz(user_id, catagory_name, session)
    if questions:
        return questions
    else:
        raise HTTPException(status_code=404, detail="question is not available")


# check the quiz availability
@app.get("/api/isQuizAvailble")
def is_Quiz_availble(catagory_name:str, session:Annotated[Session, Depends(get_session)]):
   
    return isQuizAvailble(catagory_name,session)
    
 
# get attempted catagory quiz detail
@app.get("/api/get_attempted_quiz_detail_of_spacific_catagory")
def get_attempted_quiz_detail_of_spacific_catagory(user_id:int,catagory_name:str, session:Annotated[Session, Depends(get_session)]):
    
    detail= getAttemptedQuizdetail(user_id, catagory_name, session)
    return detail

# attempt your quiz
@app.post("/api/attempt_your_quiz_")
def attempt_your_spacific_catagory_quiz(attempt_form:QuizAttemptModel, session:Annotated[Session, Depends(get_session)]):
    
    quiz_message=attempt_quiz(attempt_form, session)
    if quiz_message:
        return quiz_message
    else:
        raise HTTPException(status_code=404, detail="user not found ")


# get all user attempted quiz detail
@app.get("/api/get_attempted_quiz_detail_of_all_catagories")
def get_attempted_quiz_detail_of_all_catagories(user_id:int, session:Annotated[Session, Depends(get_session)]):
    
    data=getAllQuiz(user_id, session)
    return data
    
   

# delete the quiz for specific user
@app.delete("/api/delete_quiz")
def delete_quiz(user_id:int, catagory_id:int , session:Annotated[Session, Depends(get_session)]):
    
    message=deleteQuiz(user_id, catagory_id,session)
    return message
    


    
# Get quiz questions
@app.get("/api/get_quize_questions")
def get_quize_questions(session:Annotated[Session, Depends(get_session)]):
    statement= select(Quiz, Choices).join(Choices, isouter=True)
    questions=session.exec(statement).all()
    # data = []
    # for question in questions:
    #    choices =  get_choices(question.question_id , session)
    #    data.append(

    #     {
    #        "question" : question.question,
    #        'chocies': choices
    #     }

    #    )
    # print(questions)
    
    return "questions "
    




    

    

def start():
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)