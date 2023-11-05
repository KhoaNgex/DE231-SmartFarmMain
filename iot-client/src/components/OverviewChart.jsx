import React from "react";
import { ResponsiveLine } from "@nivo/line";
import { useTheme } from "@mui/material";
import instance from "state/axios-instance";

function formatDateString(dateString) {
  const dateObject = new Date(dateString);
  const dayOfWeek = dateObject.toLocaleString("en-US", { weekday: "short" });
  const hour = dateObject.getHours();
  const minutes = dateObject.getMinutes();
  return `${dayOfWeek}, ${hour}:${minutes}`;
}

const MyResponsiveLine = ({ data, theme }) => (
  <ResponsiveLine
    data={data}
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
    margin={{ top: 30, right: 100, bottom: 50, left: 60 }}
    xScale={{ type: "point" }}
    yScale={{
      type: "linear",
      min: 0,
      max: "auto",
      stacked: true,
      reverse: false,
    }}
    yFormat=" >-.2f"
    curve="cardinal"
    axisTop={null}
    axisRight={null}
    axisBottom={{
      tickSize: 5,
      tickPadding: 5,
      tickRotation: 45,
      format: function (value) {
        return formatDateString(value);
      },
    }}
    axisLeft={{
      tickSize: 5,
      tickPadding: 10,
      tickRotation: 0,
      legend: "Measured data",
      legendOffset: -40,
      legendPosition: "middle",
    }}
    enableGridX={false}
    colors={{ scheme: "dark2" }}
    pointSize={7}
    pointColor={{ theme: "background" }}
    pointBorderWidth={2}
    pointBorderColor={{ from: "serieColor" }}
    pointLabelYOffset={-12}
    useMesh={true}
    enableArea={true}
    legends={[
      {
        anchor: "bottom-right",
        direction: "column",
        justify: false,
        translateX: 100,
        translateY: 0,
        itemsSpacing: 0,
        itemDirection: "left-to-right",
        itemWidth: 79,
        itemHeight: 21,
        itemOpacity: 0.75,
        symbolSize: 12,
        symbolShape: "circle",
        symbolBorderColor: "rgba(0, 0, 0, .5)",
        effects: [
          {
            on: "hover",
            style: {
              itemBackground: "rgba(0, 0, 0, .03)",
              itemOpacity: 1,
            },
          },
        ],
      },
    ]}
    animate={true}
  />
);

const OverviewChart = ({ isDashboard = false, view, loc = "node1", opt }) => {
  const theme = useTheme();
  const [sensorData, setSensorData] = React.useState([]);
  const [sensorTransData, setSensorTransData] = React.useState([]);

  React.useEffect(() => {
    instance
      .get(`/sensor/${loc}`)
      .then((response) => {
        setSensorData(response.data);
        const transformedData = [];
        const propertiesToTransform =
          opt === "all" ? ["humidity", "temp", "soil", "light"] : [opt];

        for (const property of propertiesToTransform) {
          const transformedEntries = response.data.slice(-15).map((entry) => ({
            x: entry.timestamp,
            y: entry[property],
          }));

          transformedData.push({
            id: property,
            color: "hsl(328, 70%, 50%)",
            data: transformedEntries,
          });
        }
        console.log(transformedData[0]);
        setSensorTransData(transformedData);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [loc, opt]);

  return sensorTransData.length > 0 ? (
    <MyResponsiveLine data={sensorTransData} theme={theme} />
  ) : (
    <p>Loading...</p>
  );
};

export default OverviewChart;
