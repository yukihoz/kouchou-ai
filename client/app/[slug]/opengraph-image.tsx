import {OpImage, size as _size, contentType as _contentType} from './_op-image'

export const size = _size
export const contentType = _contentType

export default async function Image({ params }: { params: { slug: string } }) {
  return OpImage(params.slug)
}
