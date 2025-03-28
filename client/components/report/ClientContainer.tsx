'use client'

import {Chart} from '@/components/report/Chart'
import {Analysis} from '@/components/report/Analysis'
import React, {PropsWithChildren, useEffect, useState} from 'react'
import {Skeleton} from '@/components/ui/skeleton'
import {Cluster, Result} from '@/type'
import {LoadingBar} from '@/components/report/LoadingBar'
import {SelectChartButton} from '@/components/charts/SelectChartButton'
import {DensityFilterSettingDialog} from '@/components/report/DensityFilterSettingDialog'
import {getApiBaseUrl} from '@/app/utils/api'

type Props = {
  reportName: string
  resultSize: number
}

export function ClientContainer({reportName, resultSize, children}: PropsWithChildren<Props>) {
  const [loadedSize, setLoadedSize] = useState(0)
  const [result, setResult] = useState<Result>()
  const [filteredResult, setFilteredResult] = useState<Result>()
  const [openDensityFilterSetting, setOpenDensityFilterSetting] = useState(false)
  const [selectedChart, setSelectedChart] = useState('scatterAll')
  const [maxDensity, setMaxDensity] = useState(0.2)
  const [minValue, setMinValue] = useState(5)
  const [isFullscreen, setIsFullscreen] = useState(false)
  const [csvPath, setCsvPath] = useState<string | undefined>(undefined)


  useEffect(() => {
    fetchReport()
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])  
  

  function updateFilteredResult(maxDensity: number, minValue: number) {
    if (!result) return
    setFilteredResult({
      ...result,
      clusters: getDenseClusters(
        result.clusters || [],
        maxDensity,
        minValue
      )
    })
  }

  function onChangeDensityFilter(maxDensity: number, minValue: number) {
    setMaxDensity(maxDensity)
    setMinValue(minValue)
    if (selectedChart === 'scatterDensity') {
      updateFilteredResult(maxDensity, minValue)
    }
  }

  async function fetchReport() {
    const response = await fetch(getApiBaseUrl() + `/reports/${reportName}`, {
      headers: {
        'x-api-key': process.env.NEXT_PUBLIC_PUBLIC_API_KEY || '',
        'Content-Type': 'application/json'
      }
    })
    const reader = response.body?.getReader()
    let loaded = 0
    if (reader) {
      const chunks: Uint8Array[] = []
      while (true) {
        const {done, value} = await reader.read()
        if (done) break
        chunks.push(value)
        loaded += value.length
        setLoadedSize(loaded)
      }
      const concatenatedChunks = new Uint8Array(loaded)
      let position = 0
      for (const chunk of chunks) {
        concatenatedChunks.set(chunk, position)
        position += chunk.length
      }
      const result = new TextDecoder('utf-8').decode(concatenatedChunks)
      const r: Result = JSON.parse(result)
      setResult(r)
      setFilteredResult(r)
      if (r.csv_path) {
        setCsvPath(r.csv_path)
      }
    }
  }

  if (!result || !filteredResult) {
    return (
      <>
        <LoadingBar loaded={loadedSize} max={resultSize}/>
        <Skeleton height="534px" mb={5} mx={'auto'} w={'100%'} maxW={'1200px'}/>
        {children}
        <LoadingBar loaded={loadedSize} max={resultSize}/>
      </>
    )
  }
  return (
    <>
      {openDensityFilterSetting && (
        <DensityFilterSettingDialog
          currentMaxDensity={maxDensity}
          currentMinValue={minValue}
          onClose={() => {
            setOpenDensityFilterSetting(false)
          }}
          onChangeFilter={onChangeDensityFilter}
        />
      )}
      <SelectChartButton
        selected={selectedChart}
        onChange={(selectedChart) => {
          setSelectedChart(selectedChart)
          if (selectedChart === 'scatterAll' || selectedChart === 'treemap') {
            updateFilteredResult(1, 0)
          }
          if (selectedChart === 'scatterDensity') {
            updateFilteredResult(maxDensity, minValue)
          }
        }}
        onClickDensitySetting={() => {
          setOpenDensityFilterSetting(true)
        }}
        onClickFullscreen={() => {
          setIsFullscreen(true)
        }}
        csvPath={csvPath}
      />
      <Chart
        result={filteredResult}
        selectedChart={selectedChart}
        isFullscreen={isFullscreen}
        onExitFullscreen={() => {
          setIsFullscreen(false)
        }}
      />
      {children}
      <Analysis result={result}/>
    </>
  )
}

function getDenseClusters(clusters: Cluster[], maxDensity: number, minValue: number): Cluster[] {
  const deepestLevel = clusters.reduce((maxLevel, cluster) => Math.max(maxLevel, cluster.level), 0)
  return [
    ...clusters.filter(c => c.level !== deepestLevel),
    ...clusters.filter(c => c.level === deepestLevel).filter(c => c.density_rank_percentile <= maxDensity).filter(c => c.value >= minValue)
  ]
}
