import type { Argument, Cluster } from "@/type";
import type { PlotData } from "plotly.js";
import { ChartCore } from "./ChartCore";

type Props = {
  clusterList: Cluster[];
  argumentList: Argument[];
  onHover?: () => void;
  level: string;
  onTreeZoom: (level: string) => void;
};

export function TreemapChart({ clusterList, argumentList, onHover, level, onTreeZoom }: Props) {
  const convertedArgumentList = argumentList.map(convertArgumentToCluster);
  const list = [{ ...clusterList[0], parent: "" }, ...clusterList.slice(1), ...convertedArgumentList];
  const ids = list.map((node) => node.id);
  const labels = list.map((node) => {
    return node.id === level ? node.label.replace(/(.{50})/g, "$1<br />") : node.label.replace(/(.{15})/g, "$1<br />");
  });
  const parents = list.map((node) => node.parent);
  const values = list.map((node) => node.value);
  const customdata = list.map((node) => node.takeaway.replace(/(.{15})/g, "$1<br />"));
  const data: Partial<PlotData & { maxdepth: number; pathbar: { thickness: number } }> = {
    type: "treemap",
    ids: ids,
    labels: labels,
    parents: parents,
    values: values,
    customdata: customdata,
    level: level,
    branchvalues: "total",
    hovertemplate: "%{customdata}<extra></extra>",
    hoverlabel: {
      align: "left",
    },
    texttemplate: "%{label}<br>%{value:,}件<br>%{percentEntry:.2%}",
    maxdepth: 2,
    pathbar: {
      thickness: 28,
    },
  };

  const layout = {
    margin: { l: 10, r: 10, b: 10, t: 30 },
    colorway: [
      "#b3daa1",
      "#f5c5d7",
      "#d5e5f0",
      "#fbecc0",
      "#80b8ca",
      "#dabeed",
      "#fad1af",
      "#fbb09d",
      "#a6e3ae",
      "#f1e4d6",
    ],
  };

  return (
    <ChartCore
      data={[data]}
      layout={layout}
      useResizeHandler={true}
      style={{ width: "100%", height: "100%" }}
      config={{
        responsive: true,
        displayModeBar: false,
        locale: "ja",
      }}
      onUpdate={darkenPathbar}
      onUnhover={darkenPathbar}
      onHover={() => {
        onHover ? onHover() : null;
        darkenPathbar();
      }}
      onClick={(event) => {
        const clickedNode = event.points[0];
        const newLevel = clickedNode.data.ids[clickedNode.pointNumber]?.toString() || "0";
        onTreeZoom(newLevel);
        // 元々のクリックイベントはキャンセルされるので無限ループにはならない
      }}
    />
  );
}

function convertArgumentToCluster(argument: Argument): Cluster {
  return {
    level: 3,
    id: argument.arg_id,
    label: argument.argument,
    takeaway: "",
    value: 1,
    parent: argument.cluster_ids[2],
    density_rank_percentile: 0,
  };
}

function darkenPathbar() {
  const panels = document.querySelectorAll(".treemap > .slice > .surface");
  const leafColor = getColor(panels[panels.length - 1]);
  if (panels.length > 1) darkenColor(panels[0], leafColor);
  const pathbars = document.querySelectorAll(".treemap > .pathbar > .surface");
  for (const pathbar of pathbars) darkenColor(pathbar, leafColor);
}

function getColor(elem: Element) {
  return elem.computedStyleMap().get("fill")?.toString() || "";
}

function darkenColor(elem: Element, originalColor: string) {
  if (getColor(elem) !== originalColor) return;
  const darkenedColor = originalColor.replace(
    /rgb\((\d+), (\d+), (\d+)\)/,
    (match, r, g, b) => `rgb(${dark(r)}, ${dark(g)}, ${dark(b)})`,
  );
  const newStyle = elem.attributes.getNamedItem("style")?.value.replace(originalColor, darkenedColor) || "";
  elem.setAttribute("style", newStyle);
}

function dark(rgb: string) {
  return Math.max(0, Number.parseInt(rgb) - 30);
}
