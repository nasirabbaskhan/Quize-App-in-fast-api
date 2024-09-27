"use client";
import Link from "next/link";
import { useForm } from "react-hook-form";
import { FormType } from "@/src/components/lib/utils/type";
import { useState } from "react";
import {useRouter} from "next/navigation"

export default function page() {
const [error, setError]= useState<string>("")

  //Destructuring
  const { handleSubmit, register } = useForm<FormType>();
  const router = useRouter()

  const signup = async (data: FormType) => {
    const response= await fetch("http://localhost:8000/api/userSignup",
      {
        method:"POST",
        headers:{
          "content-type": "application/json"
        },
        body: JSON.stringify(data)
      }
    )

    if(!response.ok){
      setError(await response.json())

    }
    else{
      setError("")
      const response_data= await response.json()
      console.log("response",response_data)
      router.push("/login")
    }

   
  };
  return (
    <main className="bg-blue-300 h-screen flex content-center justify-center items-center">
      <div className="bg-green-400 px-5  py-5 w-1/3">
        <form onSubmit={handleSubmit(signup)} className="flex flex-col gap-7">
          <h1 className="text-3xl text-gray-600 text-center">
            Well Come to Quiz Hub{" "}
          </h1>
          <p className="text-xl text-red-600 ">{error?error:""}</p>
          <div>
            <p className="text-gray-500">User Name:</p>
            <input
              type="text"
              {...register("user_name", { required: true })}
          
              className="w-full py-2 rounded-md border-black bg-slate-200 px-3 shadow-sm outline-none "
              placeholder="Please Enter  Your Name"
            />
          </div>
          <div>
            <p className="text-gray-500">User Email:</p>
            <input
              type="email"
              {...register("user_email", { required: true })}
              className="w-full py-2 rounded-md border-black bg-slate-200 px-3 shadow-sm outline-none "
              placeholder="Please Enter Your Email"
            />
          </div>
          <div>
            <p className="text-gray-500">User Pasword:</p>
            <input
              type="password"
              {...register("user_password", { required: true, minLength:6 })}
           
              className="w-full py-2 rounded-md border-black bg-slate-200 px-3 shadow-sm outline-none "
              placeholder="Please Enter Your Password"
            />
          </div>

          <div>
            <button className="w-full px-2 py-2 rounded-md border shadow-lg bg-red-600 hover:bg-red-500">
              Sign Up
            </button>
          </div>

          <div>
            <p className="text-gray-600">Have Already Account</p>
            <Link href={"/login"}>
              <button className="rounded-md shadow-lg py-2 px-3 border bg-red-600 hover:bg-red-500 ">
                sign In
              </button>
            </Link>
          </div>
        </form>
      </div>
    </main>
  );
}
