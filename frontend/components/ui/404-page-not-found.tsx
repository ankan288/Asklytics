"use client";

import React from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/button";

export interface NotFoundPageProps {
  title?: string;
  subtitle?: string;
  message?: string;
  homeUrl?: string;
  buttonText?: string;
  onNavigate?: () => void;
  imageUrl?: string;
}

export function NotFoundPage({
  title = "404",
  subtitle = "Look like you're lost",
  message = "The page you are looking for is not available!",
  homeUrl = "/",
  buttonText = "Go to Home",
  onNavigate,
  imageUrl = "https://cdn.21st.dev/assets/mirror/35/354f63f88b57aceea4536df0c0cff0c3592aa46fe887ff910751fefc12f3e76c.gif",
}: NotFoundPageProps = {}) {
  const router = useRouter();

  const handleNavigate = () => {
    if (onNavigate) {
      onNavigate();
    } else {
      router.push(homeUrl);
    }
  };

  return (
    <section className="bg-white font-serif min-h-screen flex items-center justify-center">
      <div className="container mx-auto px-4">
        <div className="flex justify-center">
          <div className="w-full sm:w-10/12 md:w-8/12 text-center">
            <div
              className="h-[250px] sm:h-[350px] md:h-[400px] bg-center bg-no-repeat bg-contain"
              style={{ backgroundImage: `url(${imageUrl})` }}
              aria-hidden="true"
            >
              <h1 className="text-center text-black text-6xl sm:text-7xl md:text-8xl pt-6 sm:pt-8 font-sans font-extrabold">
                {title}
              </h1>
            </div>

            <div className="mt-[-50px]">
              <h3 className="text-2xl text-black sm:text-3xl font-bold mb-4 font-sans">
                {subtitle}
              </h3>
              <p className="mb-6 text-black sm:mb-5 font-sans">
                {message}
              </p>

              <Button
                variant="default"
                onClick={handleNavigate}
                className="my-5 bg-green-600 hover:bg-green-700 text-white font-sans font-medium"
              >
                {buttonText}
              </Button>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

export default NotFoundPage;

