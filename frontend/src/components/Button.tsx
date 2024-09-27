import React from "react";

export default function Button({
  children,
  buttonType,
}: {
  children: React.ReactNode;
  buttonType: "submit" | "reset" | "button";
}) {
  return (
    <div className="bg-red-500 py-2 px-2 text-lg border hover:bg-red-400 text-center mt-5  rounded-lg w-full">
      <button type={buttonType}>{children}</button>
    </div>
  );
}
