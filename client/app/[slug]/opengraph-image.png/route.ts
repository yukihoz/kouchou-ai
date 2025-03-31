import {OpImage} from '../_op-image'
import {generateStaticParams as _generateStaticParams} from '@/app/[slug]/page'

export async function generateStaticParams() {
  return _generateStaticParams()
}

type PageProps = {
  params: Promise<{
    slug: string
  }>
}

export async function GET(_: Request, {params}: PageProps) {
  const slug = (await params).slug
  return OpImage(slug)
}
