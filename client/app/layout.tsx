import {Provider} from '@/components/ui/provider'
import './global.css'
import {getImageFromServerSrc} from '@/app/utils/image-src'
import Script from 'next/script'

const enableGA = !!process.env.NEXT_PUBLIC_GA_MEASUREMENT_ID && 
  (process.env.ENVIRONMENT === 'production' || process.env.NODE_ENV === 'production')

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang={'ja'}>
      <head>
        <link rel={'icon'} href={getImageFromServerSrc('/meta/icon.png')} sizes={'any'}/>
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
        <Provider>
          {children}
        </Provider>
      </body>
    </html>
  )
}
