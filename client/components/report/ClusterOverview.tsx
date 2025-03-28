import {Cluster} from '@/type'
import {Box, Heading, Text} from '@chakra-ui/react'
import {MessagesSquareIcon} from 'lucide-react'

type Props = {
  cluster: Cluster
}

export function ClusterOverview({cluster}: Props) {
  return (
    <Box mx={'auto'} maxW={'750px'} mb={12}>
      <Box mb={2}>
        <Heading fontSize={'2xl'} className={'headingColor'} mb={1}>{cluster.label}</Heading>
        <Text fontWeight={'bold'} display='flex' gap={1}>
          <MessagesSquareIcon size={20}/>
          {cluster.value.toLocaleString()}件
        </Text>
      </Box>
      <Text>{cluster.takeaway}</Text>
    </Box>
  )
}
