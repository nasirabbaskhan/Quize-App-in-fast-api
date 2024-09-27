"use client";
import Button from "@/src/components/Button";
import { useForm } from "react-hook-form";
import { FormType } from "@/src/components/lib/utils/type";
import Link from "next/link";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { setCookie } from 'cookies-next';




export default function page() {

  // destructuring
  const { register, handleSubmit } = useForm<FormType>();
  const router = useRouter()


  // useState
  const [error, setError]= useState("")

  
  const loginFn = async (data: FormType) => {
    const response= await fetch("http://localhost:8000/api/signin",
      {
        method: "POST",
         headers:{
          "content-type": "application/json"
         },
         body:JSON.stringify(data)

      })

      if (!response.ok){
        setError(await response.json())
      }
      else{
        setError("")
        const token_data= await response.json() // response data
        console.log("response",token_data)

        const {access_token, refresh_token}= token_data
        
        
        /* 
        here access_expiration_time hase present time in month/day/year/h/mm/sc
        but we want the prsent time only in second 
        we want to add present sconds into expiry_time of user token
        eg: if presennt second is 10 and expiry time is 20 seconds so 10+20 =30 after 30 second the expiry time will be end
        for that reason we need to set the present time into second and add it with expiry time 
      */
        // add the present time in second and access_expirey_time

        const access_expiration_time = new Date()
        access_expiration_time.setSeconds(access_expiration_time.getSeconds() + access_token.access_expiry_time) 
        
        // console.log("access_time",access_token.access_expiry_time) 
        // console.log("access_expiration_time",access_expiration_time.getSeconds())  
        // console.log("expiration_time",access_expiration_time)  

        const refresh_expiration_time = new Date()
        refresh_expiration_time.setSeconds(refresh_expiration_time.getSeconds() + refresh_token.refresh_expiry_time) 
         

        // set the access_token in cookie
         setCookie("access_token", access_token.token,{
          expires: access_expiration_time,
          secure:true,
          sameSite:'strict'
         })

        // set the access_token in cookie
         setCookie("refresh_token", refresh_token.token,{
          expires: refresh_expiration_time,
          secure:true,
          sameSite:'strict'
         })
                 
        
        router.push("/")
      }    
    

  };

  return (
    <main className="h-screen flex flex-col justify-center items-center gap-10  bg-gradient-to-tr from-black via-slate-950 to-blue-950">
      
      <div className="w-1/3 bg-green-500 py-6 px-6 rounded-md shadow-sm mt-10 ">
      <h1 className=" text-2xl text-center mt-1 text-gray-700">
        Well Come to Quiz Hub
      </h1>
      <p className="text-md   text-red-700">{error?error:""}</p>
        <form
          onSubmit={handleSubmit(loginFn)}
          className=" flex flex-col gap-6 py-6"
        >
        
          <div>
            <p className="text-slate-600">User Email:</p>
            <input
              type="email"
              {...register("user_email", { required: true })}
              placeholder="please Enter Email"
              className="bg-slate-300 py-2 w-full outline-none  px-1 rounded-md "
            />
          </div>
          <div>
            <p className="text-slate-600">Password</p>
            <input
              type="password"
              {...register("user_password", { required: true, minLength: 6 })}
              placeholder="please Enter Your Password"
              className="bg-slate-300 py-2 w-full outline-none  px-1 rounded-md "
            />
          </div>
          <div className="btn">
            <button className="bg-red-500 py-2 px-2 text-lg border hover:bg-red-400 mt-5 rounded-lg w-full">Sign In</button>
          </div>
          {/* <Button buttonType="submit">Sign In</Button> */}

          <div>
          <p className="  text-gray-700">Don't have account</p>
          <Link href={"/register"}>
          <button className="bg-red-500 py-2 px-3  border hover:bg-red-400  rounded-lg shadow-xl  ">Sign Up</button>
          </Link>
       </div>
        </form>
       
      </div>
    </main>
  );
}


  