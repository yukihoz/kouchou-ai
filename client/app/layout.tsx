import {Provider} from '@/components/ui/provider'
import './global.css'
import {getImageFromServerSrc} from '@/app/utils/image-src'

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang={'ja'}>
      <head>
        <link rel={'icon'} href={getImageFromServerSrc('/meta/icon.png')} sizes={'any'}/>
      </head>
      <body>
        <Provider>
          {children}
        </Provider>
      </body>
    </html>
  )
}
