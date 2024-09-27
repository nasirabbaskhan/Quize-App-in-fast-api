from typing import Optional
from sqlmodel import Relationship, SQLModel, Field

class Catagory(SQLModel, table=True):
    __tablename__ = 'catagory'  # Explicitly define the table name
    catagory_id:int|None= Field(default=None, primary_key=True)
    catagory_name:str
    catagory_description:str
    
class CreateCatagory(SQLModel):
    catagory_name:str
    catagory_description:str 
    
# class UpdateCatagory_data(SQLModel):
#     catagory_name:str | None
#     catagory_description:str  |None
    
       
# class QuizLevel(SQLModel, table=True):
#     __tablename__ = 'quizLevel'  # Explicitly define the table name
#     quiz_level_id:int| None= Field(default=None, primary_key=True)
#     quiz_level:str 
#     catagory_id:int = Field(foreign_key="catagory.catagory_id")
    
# class CreatQuizLevel(SQLModel):
#     quiz_level:str 
#     catagory_id:int 
    
    
    
class Quiz(SQLModel, table=True):
    __tablename__ = 'quiz'  # Explicitly define the table name
    question_id:int|None = Field(default=None,primary_key=True)
    question:str
    catagory_id:int = Field(foreign_key="catagory.catagory_id")
    questions: list["Choices"] = Relationship(back_populates="choices") # here is question choices
    
    
class Choices(SQLModel, table=True):
    __tablename__ = 'choices'  # Explicitly define the table name
    choice_id:int|None= Field(default=None, primary_key=True) 
    choice:str
    status:bool= False  
    question_id: Optional[int]= Field(None, foreign_key="quiz.question_id")
    choices: Quiz | None = Relationship(back_populates="questions")
    
class Create_Quiz(SQLModel):
    question:str
    # question_id:int | None
    catagory_id:int
    choice1: str
    choice1_status: bool = False
    choice2: str
    choice2_status: bool = False
    choice3: str
    choice3_status: bool = False
    
class CategoryMarks(SQLModel, table=True):
    """Model for marks obtained in quiz categories."""
    id: int | None = Field(None, primary_key=True)
    category_id: int = Field(int, foreign_key="catagory.catagory_id")  # ID of the category
    marks: int = 50  # Marks obtained

class InsertCatagoryMasrks(SQLModel):
    category_id: int
    marks: int 
    
    
    
class CategoryQuizDetails(SQLModel, table=True):
    """Model for details of quizzes taken by users in specific categories."""
    id: Optional[int] = Field(None, primary_key=True)
    user_id: int = Field(foreign_key="user.user_id")  # ID of the user
    category_id: int = Field( foreign_key="catagory.catagory_id")  # ID of the category
    obtaining_marks: int   # Marks obtained in the quiz
    percentage:int = Field(0, le=100)  # Percentage score
    rank: Optional[str] = None  # Rank achieved
    remaining_questions: int = Field(default=10)  # Number of remaining questions (default is 10)
    is_finished: bool = Field(default=False)  # Flag indicating if the quiz is finished (default is False)
    
class QuizAttemptModel(SQLModel):
    user_id: int
    category_id: int
    obtaining_marks: int
    isFinished: bool = False