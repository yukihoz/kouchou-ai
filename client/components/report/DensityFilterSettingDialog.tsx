import {
  DialogBody,
  DialogCloseTrigger,
  DialogContent,
  DialogFooter,
  DialogHeader,
  DialogRoot,
  DialogTitle,
} from "@/components/ui/dialog";
import { Slider } from "@/components/ui/slider";
import { Box, Button, Spacer, Text } from "@chakra-ui/react";
import React, { useState } from "react";

type Props = {
  onClose: () => void;
  onChangeFilter: (maxDensity: number, minValue: number) => void;
  currentMaxDensity: number;
  currentMinValue: number;
};

export function DensityFilterSettingDialog({
  onClose,
  onChangeFilter,
  currentMaxDensity,
  currentMinValue,
}: Props) {
  const [maxDensity, setMaxDensity] = useState(currentMaxDensity);
  const [minValue, setMinValue] = useState(currentMinValue);

  function onApply() {
    onChangeFilter(maxDensity, minValue);
    onClose();
  }

  return (
    <DialogRoot lazyMount open={true} onOpenChange={onClose}>
      <DialogContent>
        <DialogHeader>
          <DialogTitle>濃い意見グループ設定</DialogTitle>
          <Text>
            濃い意見グループ設定を設定すると、表示件数を絞って詳細を確認できます
            <br />
            （全体図には適用されません）
          </Text>
        </DialogHeader>
        <DialogBody>
          <Box mb={4}>
            <Slider
              label={`上位何％の意見グループを表示するか: ${maxDensity * 100}%`}
              step={0.1}
              min={0.1}
              max={1}
              value={[maxDensity]}
              onValueChange={(e) => setMaxDensity(Number(e.value[0]))}
              marks={[
                { value: 0.1, label: "10%" },
                { value: 1, label: "100%" },
              ]}
            />
          </Box>
          <Box>
            <Slider
              label={`意見グループのサンプル数の最小数: ${minValue}`}
              step={1}
              min={0}
              max={10}
              value={[minValue]}
              onValueChange={(e) => setMinValue(Number(e.value[0]))}
              marks={[
                { value: 0, label: "0" },
                { value: 10, label: "10" },
              ]}
            />
          </Box>
        </DialogBody>
        <DialogFooter justifyContent={"space-between"}>
          <Spacer />
          <Box>
            <Button onClick={onApply}>設定を適用</Button>
          </Box>
        </DialogFooter>
        <DialogCloseTrigger />
      </DialogContent>
    </DialogRoot>
  );
}
