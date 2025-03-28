import {Provider} from '@/components/ui/provider'
import './global.css'
import {getImageSrcFromServer} from '@/components/ui/image-from-server'

export default function RootLayout({children}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html suppressHydrationWarning lang={'ja'}>
      <head>
        <link rel={'icon'} href={getImageSrcFromServer('/meta/icon.png')} sizes={'any'}/>
      </head>
      <body>
        <Provider>
          {children}
        </Provider>
      </body>
    </html>
  )
}
