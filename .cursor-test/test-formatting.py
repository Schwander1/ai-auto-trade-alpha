# Test file for Cursor formatting verification
# This file tests Python formatting with Black

def   test_function(  param1,param2,param3  ):
    """Test function with bad formatting"""
    x=1+2+3
    y=  "hello"  +  "world"
    return   x,y

class   TestClass:
    def   __init__(self):
        self.value=42
        self.name="test"

# This should be formatted on save
if __name__=="__main__":
    obj=TestClass()
    result=test_function(1,2,3)
    print(result)
