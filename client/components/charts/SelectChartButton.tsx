import {RadioCardItem, RadioCardRoot} from '@/components/ui/radio-card'
import {Button, HStack, Icon, useBreakpointValue} from '@chakra-ui/react'
import {ChartScatterIcon, CogIcon, FullscreenIcon, MessageCircleWarningIcon, SquareSquareIcon, DownloadIcon} from 'lucide-react'
import React from 'react'
import {Tooltip} from '@/components/ui/tooltip'
import {getApiBaseUrl} from '@/app/utils/api'

type Props = {
  selected: string
  onChange: (value: string) => void
  onClickDensitySetting: () => void
  onClickFullscreen: () => void
  csvPath?: string
}

export function SelectChartButton({selected, onChange, onClickDensitySetting, onClickFullscreen, csvPath}: Props) {
  return (
    <HStack
      w={'100%'}
      maxW={'1200px'}
      mx={'auto'}
      justify={'space-between'}
      align={'center'}
      mb={2}
    >
      <RadioCardRoot
        orientation="horizontal"
        align="center"
        justify="center"
        w={'100%'}
        maxW={'xl'}
        size={'sm'}
        display={'block'}
        value={selected}
        onChange={(e: React.ChangeEvent<HTMLInputElement>) => onChange(e.target.value)}
        colorPalette={'cyan'}
      >
        <HStack align={'stretch'}>
          <RadioCardItem
            value={'scatterAll'}
            label={useBreakpointValue({base: '', md: '全体図'})}
            indicator={false}
            icon={<Icon><ChartScatterIcon/></Icon>}
            cursor={'pointer'}
          />
          <RadioCardItem
            value={'scatterDensity'}
            label={useBreakpointValue({base: '', md: '濃い意見グループ'})}
            indicator={false}
            icon={<Icon><MessageCircleWarningIcon/></Icon>}
            cursor={'pointer'}
          />
          <RadioCardItem
            value={'treemap'}
            label={useBreakpointValue({base: '', md: '階層図'})}
            indicator={false}
            icon={<Icon><SquareSquareIcon/></Icon>}
            cursor={'pointer'}
          />
        </HStack>
      </RadioCardRoot>
      <HStack>
        {csvPath && (
          <Tooltip content={'CSVファイルをダウンロード'} openDelay={0} closeDelay={0}>
            <Button
              onClick={async () => {
                try {
                  const response = await fetch(getApiBaseUrl() + `/get-csv/${csvPath}`, {
                    headers: {
                      'x-api-key': process.env.NEXT_PUBLIC_PUBLIC_API_KEY || '',
                      'Content-Type': 'application/json'
                    }
                  })
                  if (!response.ok) {
                    throw new Error('CSVダウンロード失敗')
                  }
                  const blob = await response.blob()
                  const url = window.URL.createObjectURL(blob)
                  const link = document.createElement('a')
                  link.href = url
                  link.download = `kouchou_${csvPath}.csv`
                  link.click()
                  window.URL.revokeObjectURL(url)
                } catch (error) {
                  console.error(error)
                  alert('CSVのダウンロードに失敗しました')
                }
              }}
              variant={'outline'}
              h={'50px'}
            >
              <Icon><DownloadIcon/></Icon>
            </Button>
          </Tooltip>
        )}

      </HStack>

      <HStack>
        <Tooltip content={'濃い意見グループ設定'} openDelay={0} closeDelay={0}>
          <Button
            onClick={onClickDensitySetting}
            variant={'outline'}
            h={'50px'}
          >
            <Icon><CogIcon/></Icon>
          </Button>
        </Tooltip>
        <Tooltip content={'全画面表示'} openDelay={0} closeDelay={0}>
          <Button
            onClick={onClickFullscreen}
            variant={'outline'}
            h={'50px'}
          >
            <Icon><FullscreenIcon/></Icon>
          </Button>
        </Tooltip>
      </HStack>
    </HStack>
  )
}
