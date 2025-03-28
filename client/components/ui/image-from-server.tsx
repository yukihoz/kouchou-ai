import { Image, ImageProps } from '@chakra-ui/react'

export const ImageFromServer = ({ src, alt, ...props }: ImageProps) => {
  const basePath = process.env.NEXT_PUBLIC_API_BASEPATH || ''
  let _src = new URL(src || '', basePath).href

  if (process.env.NEXT_PUBLIC_OUTPUT_MODE === 'export' && src) {
    _src = src
  }

  return <Image src={_src} alt={alt} {...props} />
}
