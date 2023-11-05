import React from "react";
import { ResponsivePie } from "@nivo/pie";
import { Box, Typography, useTheme } from "@mui/material";
import instance from "state/axios-instance";

function countSignalOccurrences(objects, colors) {
  let countSignal0 = 0;
  let countSignal1 = 0;

  objects.forEach((obj) => {
    if (obj.signal === 0) {
      countSignal0++;
    } else if (obj.signal === 1) {
      countSignal1++;
    }
  });

  const cntSignal = {
    salesByCategory: {
      signal_on: countSignal1,
      signal_off: countSignal0,
    },
    total: countSignal1 + countSignal0,
  };

  const reformattedData = [];
  const entries = Object.entries(cntSignal.salesByCategory);
  for (let i = 0; i < entries.length; i++) {
    const [category, cnt] = entries[i];
    reformattedData.push({
      id: category,
      label: category,
      value: cnt,
      color: colors[i],
    });
  }

  return { cntSignal, reformattedData };
}

const BreakdownChart = ({ isDashboard = false, loc = "node1" }) => {
  const theme = useTheme();
  const colors = [
    theme.palette.secondary[500],
    theme.palette.secondary[300],
    theme.palette.secondary[300],
    theme.palette.secondary[500],
  ];

  const [pumpData, setPumpData] = React.useState([]);
  const [pumpStats, setPumpStats] = React.useState({});
  const [formattedData, setFormattedData] = React.useState([]);

  React.useEffect(() => {
    instance
      .get(`/pump/${loc}`)
      .then((response) => {
        setPumpData(response.data);
        let { cntSignal, reformattedData } = countSignalOccurrences(
          response.data, colors
        );
        setPumpStats(cntSignal);
        setFormattedData(reformattedData);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [loc]);

  return (
    <Box
      height={isDashboard ? "400px" : "100%"}
      width={undefined}
      minHeight={isDashboard ? "325px" : undefined}
      minWidth={isDashboard ? "325px" : undefined}
      position="relative"
    >
      {pumpData.length > 0 ? (
        <>
          <ResponsivePie
            data={formattedData}
            theme={{
              axis: {
                domain: {
                  line: {
                    stroke: theme.palette.secondary[200],
                  },
                },
                legend: {
                  text: {
                    fill: theme.palette.secondary[200],
                  },
                },
                ticks: {
                  line: {
                    stroke: theme.palette.secondary[200],
                    strokeWidth: 1,
                  },
                  text: {
                    fill: theme.palette.secondary[200],
                  },
                },
              },
              legends: {
                text: {
                  fill: theme.palette.secondary[200],
                },
              },
              tooltip: {
                container: {
                  color: theme.palette.primary.main,
                },
              },
            }}
            colors={{ datum: "data.color" }}
            margin={
              isDashboard
                ? { top: 40, right: 80, bottom: 100, left: 50 }
                : { top: 40, right: 80, bottom: 80, left: 80 }
            }
            sortByValue={true}
            innerRadius={0.45}
            activeOuterRadiusOffset={8}
            borderWidth={1}
            borderColor={{
              from: "color",
              modifiers: [["darker", 0.2]],
            }}
            enableArcLinkLabels={!isDashboard}
            arcLinkLabelsTextColor={theme.palette.secondary[200]}
            arcLinkLabelsThickness={2}
            arcLinkLabelsColor={{ from: "color" }}
            arcLabelsSkipAngle={10}
            arcLabelsTextColor={{
              from: "color",
              modifiers: [["darker", 2]],
            }}
            legends={[
              {
                anchor: "bottom",
                direction: "row",
                justify: false,
                translateX: isDashboard ? 20 : 0,
                translateY: isDashboard ? 50 : 56,
                itemsSpacing: 0,
                itemWidth: 85,
                itemHeight: 18,
                itemTextColor: "#999",
                itemDirection: "left-to-right",
                itemOpacity: 1,
                symbolSize: 18,
                symbolShape: "circle",
                effects: [
                  {
                    on: "hover",
                    style: {
                      itemTextColor: theme.palette.primary[500],
                    },
                  },
                ],
              },
            ]}
          />
          <Box
            position="absolute"
            top="50%"
            left="50%"
            color={theme.palette.secondary[400]}
            textAlign="center"
            pointerEvents="none"
            sx={{
              transform: isDashboard
                ? "translate(-75%, -170%)"
                : "translate(-50%, -100%)",
            }}
          >
            <Typography variant="h6">
              {!isDashboard && "Total:"} Total: {pumpStats.total}
            </Typography>
          </Box>
        </>
      ) : (
        <Box sx={{
          display: 'flex',
          justifyContent: "center",
          alignItems: "center",
          width: "100%"
        }}>
          <p>Loading...</p>
        </Box>
      )}
    </Box>
  );
};

export default BreakdownChart;
