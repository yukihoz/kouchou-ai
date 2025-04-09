import ClientProvider from "./ClientProvider";
import "./global.css";
import { Toaster } from "@/components/ui/toaster";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "デジタル民主主義2030ブロードリスニング",
  robots: {
    index: false,
    follow: false,
  },
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang={"ja"}>
      <head>
        <link
          rel={"icon"}
          href={`${process.env.NEXT_PUBLIC_API_BASEPATH}/meta/icon.png`}
          sizes={"any"}
        />
      </head>
      <body>
        <ClientProvider>
          {children}
          <Toaster />
        </ClientProvider>
        <footer>デジタル民主主義2030プロジェクト</footer>
      </body>
    </html>
  );
}
