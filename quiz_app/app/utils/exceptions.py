# errors 
# generate custom exception (errors)

#only class with constructor
class InvalidInputException(Exception):
    def __init__(self, args:str):
        self.invalid_input= args
    
    
class NotFoundException(Exception):
    def __init__(self,args:str):
        self.not_found= args
   
    
    
class ConflictException(Exception):
    def __init__(self,args:str):
        self.conflict_input= args
    

