// Test file for Cursor formatting verification
// This file tests TypeScript/React formatting with Prettier

import React from 'react';

interface   TestProps{
  name:string;
  age:number;
}

export   const   TestComponent:React.FC<TestProps>=({name,age})=>{
  const   message=`Hello ${name}, you are ${age} years old`;

  return(
    <div   className="test-container">
      <h1>{message}</h1>
      <button   onClick={()=>console.log('clicked')}>
        Click Me
      </button>
    </div>
  );
};

// This should be formatted on save
const   App=()=>{
  return<TestComponent name="Test" age={25}/>;
};

export default App;
