import type { Metadata } from "next";
import { Fira_Code, Inter } from "next/font/google";
import Nav from "@/components/Nav";
import "./globals.css";

const firaCode = Fira_Code({
  subsets: ["latin"],
  variable: "--font-fira-code",
});

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "Dispute Triage Agent",
  description: "LangGraph + Claude agent that triages chargeback disputes and drafts representment letters.",
};

export default function RootLayout({ children }: LayoutProps<"/">) {
  return (
    <html lang="en" className={`${firaCode.variable} ${inter.variable} h-full antialiased`}>
      <body className="min-h-full bg-bg p-4 text-text">
        <div className="relative mx-auto min-h-[calc(100vh-2rem)] max-w-5xl overflow-x-hidden rounded-sm border-2 border-text/40 px-6 py-6 shadow-[4px_4px_0_0_var(--color-highlight)]">
          <Nav />
          {children}
        </div>
      </body>
    </html>
  );
}
