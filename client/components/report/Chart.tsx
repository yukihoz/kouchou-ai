import { ScatterChart } from "@/components/charts/ScatterChart";
import { TreemapChart } from "@/components/charts/TreemapChart";
import { Tooltip } from "@/components/ui/tooltip";
import type { Result } from "@/type";
import { Box, Button, Icon } from "@chakra-ui/react";
import { Undo2Icon } from "lucide-react";
import React from "react";

type ReportProps = {
  result: Result;
  selectedChart: string;
  isFullscreen: boolean;
  onExitFullscreen: () => void;
};

export function Chart({
  result,
  selectedChart,
  isFullscreen,
  onExitFullscreen,
}: ReportProps) {
  if (isFullscreen) {
    return (
      <Box
        w={"100%"}
        h={"100vh"}
        position={"fixed"}
        top={0}
        bottom={0}
        left={0}
        right={0}
        bgColor={"#fff"}
      >
        <Tooltip content={"全画面終了"} openDelay={0} closeDelay={0}>
          <Button
            onClick={onExitFullscreen}
            h={"50px"}
            position={"fixed"}
            top={5}
            right={5}
            zIndex={1}
            borderWidth={2}
          >
            <Icon>
              <Undo2Icon />
            </Icon>
          </Button>
        </Tooltip>
        {(selectedChart === "scatterAll" ||
          selectedChart === "scatterDensity") && (
          <ScatterChart
            clusterList={result.clusters}
            argumentList={result.arguments}
            targetLevel={
              selectedChart === "scatterAll"
                ? 1
                : Math.max(...result.clusters.map((c) => c.level))
            }
          />
        )}
        {selectedChart === "treemap" && (
          <TreemapChart
            clusterList={result.clusters}
            argumentList={result.arguments}
          />
        )}
      </Box>
    );
  }

  return (
    <Box mx={"auto"} w={"100%"} maxW={"1200px"} mb={10}>
      <Box h={"500px"} mb={5}>
        {selectedChart === "treemap" && (
          <TreemapChart
            clusterList={result.clusters}
            argumentList={result.arguments}
          />
        )}
        {(selectedChart === "scatterAll" ||
          selectedChart === "scatterDensity") && (
          <ScatterChart
            clusterList={result.clusters}
            argumentList={result.arguments}
            targetLevel={
              selectedChart === "scatterAll"
                ? 1
                : Math.max(...result.clusters.map((c) => c.level))
            }
          />
        )}
      </Box>
    </Box>
  );
}
