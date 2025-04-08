import ClientProvider from './ClientProvider'
import './global.css'
import {Toaster} from '@/components/ui/toaster'
import {Metadata} from 'next'
import Script from 'next/script'

export const metadata: Metadata = {
  title: 'デジタル民主主義2030ブロードリスニング',
  robots: {
    index: false,
    follow: false
  }
}

const enableGA = !!process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID && 
  (process.env.ENVIRONMENT === 'production' || process.env.NODE_ENV === 'production')

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang={'ja'}>
      <head>
        <link rel={'icon'} href={process.env.NEXT_PUBLIC_API_BASEPATH + '/meta/icon.png'} sizes={'any'}/>
        {enableGA && (
          <>
            <Script 
              src={`https://www.googletagmanager.com/gtag/js?id=${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}`} 
              strategy="afterInteractive" 
            />
            <Script id="google-analytics" strategy="afterInteractive">
              {`
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', '${process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID}');
              `}
            </Script>
          </>
        )}
      </head>
      <body>
        <ClientProvider>
          {children}
          <Toaster/>
        </ClientProvider>
        <footer>デジタル民主主義2030プロジェクト</footer>
      </body>
    </html>
  )
}
