from app.controller.auth_controller import generate_admin_token, generateAccessAndRefreshToken, generateToken, passwordIntoHash, varifyPassword
from app.model.admin_models import Admin, AdminLogin, AdminSignup, AdminToken
from typing import Annotated
from fastapi import Depends, HTTPException
from sqlmodel import Session,select
from app.db.db_connector import get_session
from app.model.quiz_models import Catagory, CategoryMarks, Choices, Create_Quiz, InsertCatagoryMasrks, Quiz
from app.setting import access_expiry_time , refresh_expiry_time


def AdminsignUpFn(form_data:AdminSignup,session:Annotated[Session, Depends(get_session)]):
    admins=session.exec(select(Admin)).all()
    
    for admin in admins:
        is_email_exist= admin.admin_email==form_data.admin_email
        is_password_xist= varifyPassword(form_data.admin_password,admin.admin_password)
        if is_email_exist and is_password_xist:
            raise HTTPException(status_code=404, detail="Email and password already exist")
        elif is_email_exist:
            raise  HTTPException(status_code=404, detail="email already exist")
        elif is_password_xist:
            raise HTTPException(status_code=404, detail="password is already exist")
        # varifying Admin is exist already or not
    
    # # gnerate hash password
    hasedPasword=passwordIntoHash(form_data.admin_password)
    # add the  new admin in DB
    admin=Admin(admin_name=form_data.admin_name, admin_email=form_data.admin_email,admin_password=hasedPasword)
    session.add(admin)
    session.commit()
    session.refresh(admin)
    
    if admin:
        return admin
        
    else:
        raise HTTPException(status_code=404, detail="admin is not exist")
    
    
    
# admin login fun
def adminLoginFn(login_form:AdminLogin, session:Annotated[Session, Depends(get_session)]):
    admins= session.exec(select(Admin))
    
    for admin in admins:
        #verify email and possword is exist
        is_email_exist= admin.admin_email==login_form.admin_email
        is_pasword_exist= varifyPassword(login_form.admin_password, admin.admin_password)
        if is_email_exist and is_pasword_exist:
            # generate the admin access token
            
            data= {
                "admin_name":admin.admin_name,
                "admin_email": admin.admin_email,
       
            }
            
            admin_token=generate_admin_token(data,expires_delta=access_expiry_time)
            
            existing_user_token=session.exec(select(AdminToken).where(AdminToken.admin_id==admin.admin_id)).first()
            
            if existing_user_token:
               # update the existing_user_token
                existing_user_token.admin_token= admin_token
               
                session.add(existing_user_token)
                session.commit()
                session.refresh(existing_user_token)
                return  {
                "admin_token": existing_user_token.admin_token,
                "admin_token_id": existing_user_token.admin_tokenId,
                "expiry_time": access_expiry_time
            }
            else:
                # if not exist the add
                # note this part you can do at signup time
                token=AdminToken(admin_token=admin_token, admin_id=admin.admin_id)
                session.add(token)
                session.commit()
                session.refresh(token)
                return  {
                "admin_token": token.admin_token,
                "admin_token_id": token.admin_tokenId,
                "expiry_time": access_expiry_time
                }
            
        else:
            raise HTTPException(status_code=404, detail="Email or password is not exist")
            
    
def insert_question(questions_form:Create_Quiz, session:Annotated[Session, Depends(get_session)]):
    if not questions_form:
        raise HTTPException(status_code=404, detail="Questions data is missing")
    # varify catagory of question is exist
    db_catagory=session.exec(select(Catagory).where(Catagory.catagory_id==questions_form.catagory_id)).first()
    if db_catagory is None:
        raise HTTPException(status_code=404, detail=("catagory id is not exist"))
    
    choice1=Choices(choice=questions_form.choice1,status=questions_form.choice1_status)
    choice2= Choices(choice=questions_form.choice2, status=questions_form.choice2_status)
    choice3= Choices(choice=questions_form.choice3, status=questions_form.choice3_status)
    
    new_question=Quiz(question=questions_form.question,catagory_id=questions_form.catagory_id, questions=[choice1, choice2, choice3])
    
    session.add(new_question)
    session.commit()
    session.refresh(new_question)
    
    return new_question



    
def insrt_catagory_marks(marks_form:InsertCatagoryMasrks, session:Annotated[Session, Depends(get_session)]):
    if not marks_form:
        raise HTTPException(status_code=404, detail="catagory id or marks input field missing")
    
    # varify catagory is exist 
    db_catagory= session.exec(select(Catagory).where(Catagory.catagory_id==marks_form.category_id)).first()
    
    if db_catagory is None:
        raise HTTPException(status_code=404, detail="catagory id is not exist")
    
    new_ctagory_marks= CategoryMarks(category_id=marks_form.category_id, marks=marks_form.marks)
    session.add(new_ctagory_marks)
    session.commit()
    session.refresh(new_ctagory_marks)
    return new_ctagory_marks
    
    
    
    
    
        
    