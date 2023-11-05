import React from "react";
import FlexBetween from "components/FlexBetween";
import Header from "components/Header";
import { DownloadOutlined } from "@mui/icons-material";
import DeviceThermostatIcon from "@mui/icons-material/DeviceThermostat";
import Brightness6Icon from "@mui/icons-material/Brightness6";
import GrassIcon from "@mui/icons-material/Grass";
import GrainIcon from "@mui/icons-material/Grain";
import {
  Box,
  Button,
  Typography,
  useTheme,
  useMediaQuery,
  FormControl,
  InputLabel,
  Select,
  MenuItem,
} from "@mui/material";
import { DataGrid } from "@mui/x-data-grid";
import BreakdownChart from "components/BreakdownChart";
import OverviewChart from "components/OverviewChart";
import StatBox from "components/StatBox";
import instance from "state/axios-instance";

const pump_data = [
  {
    _id: "63701d74f03239c72c000192",
    userId: "63701cc1f032390a34000319",
    cost: 3584.18,
    createdAt: "1983-01-10T18:53:05.874Z",
  },
  {
    _id: "63701d74f03239c72c000193",
    userId: "63701cc1f032398675000129",
    cost: 2872.78,
    createdAt: "1983-01-10T18:53:05.874Z",
  },
];

const Dashboard = () => {
  const theme = useTheme();
  const isNonMediumScreens = useMediaQuery("(min-width: 1200px)");

  const columns = [
    {
      field: "signal",
      headerName: "Pump Action",
      flex: 1,
      align: "center",
      headerAlign: "center",
      renderCell: (params) => <div>{params.value === 1 ? "On" : "Off"}</div>,
    },
    {
      field: "timestamp",
      headerName: "Recorded At",
      flex: 1,
      align: "center",
      headerAlign: "center",
    },
  ];

  const [loc, setLoc] = React.useState("node1");
  const [opt, setOpt] = React.useState("temp");

  const handleChangeLoc = (event) => {
    setLoc(event.target.value);
  };
  const handleChangeOpt = (event) => {
    setOpt(event.target.value);
  };

  const [pumpData, setPumpData] = React.useState([]);
  const [sensorData, setSensorData] = React.useState([]);

  React.useEffect(() => {
    instance
      .get(`/pump/${loc}`)
      .then((response) => {
        setPumpData(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [loc]);

  React.useEffect(() => {
    instance
      .get(`/sensor/${loc}`)
      .then((response) => {
        setSensorData(response.data);
      })
      .catch((error) => {
        console.error(error);
      });
  }, [loc]);

  return (
    <Box m="1.5rem 2.5rem">
      <FlexBetween>
        <Header title="IOT DASHBOARD" subtitle="Welcome, choose your area..." />
        <Box
          sx={{
            display: "flex",
            flexDirection: "row",
            gap: 2,
            alignItems: "center",
          }}
        >
          <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
            <InputLabel id="demo-simple-select-standard-label">Area</InputLabel>
            <Select
              labelId="demo-simple-select-standard-label"
              id="demo-simple-select-standard"
              value={loc}
              onChange={handleChangeLoc}
              label="Area"
            >
              <MenuItem value={"node1"}>Cherry Farm</MenuItem>
              <MenuItem value={"node2"}>Apple Farm</MenuItem>
            </Select>
          </FormControl>
          <FormControl variant="standard" sx={{ m: 1, minWidth: 120 }}>
            <InputLabel id="demo-simple-select-standard-label-1">
              Sensor
            </InputLabel>
            <Select
              labelId="demo-simple-select-standard-label-1"
              id="demo-simple-select-standard-1"
              value={opt}
              onChange={handleChangeOpt}
              label="Sensor"
            >
              <MenuItem value={"temp"}>Temperature</MenuItem>
              <MenuItem value={"humidity"}>Humidity</MenuItem>
              <MenuItem value={"soil"}>Soil</MenuItem>
              <MenuItem value={"light"}>Light</MenuItem>
              <MenuItem value={"all"}>All</MenuItem>
            </Select>
          </FormControl>
          <Box>
            <Button
              sx={{
                backgroundColor: theme.palette.secondary.light,
                color: theme.palette.background.alt,
                fontSize: "14px",
                fontWeight: "bold",
                padding: "10px 20px",
                "&:hover": {
                  backgroundColor: theme.palette.secondary.dark,
                },
              }}
            >
              <DownloadOutlined sx={{ mr: "10px" }} />
              Download Reports
            </Button>
          </Box>
        </Box>
      </FlexBetween>

      <Box
        mt="20px"
        display="grid"
        gridTemplateColumns="repeat(12, 1fr)"
        gridAutoRows="160px"
        gap="20px"
        sx={{
          "& > div": { gridColumn: isNonMediumScreens ? undefined : "span 12" },
        }}
      >
        {/* ROW 1 */}
        {sensorData.length > 0 ? (
          <>
            <StatBox
              title="Temperature"
              value={Math.round(sensorData[sensorData.length - 1].temp)}
              unit="&deg;C"
              increase="+2"
              description={sensorData[sensorData.length - 1].timestamp}
              icon={
                <DeviceThermostatIcon
                  sx={{ color: theme.palette.secondary[300], fontSize: "26px" }}
                />
              }
            />
            <StatBox
              title="Humidity"
              value={sensorData[sensorData.length - 1].humidity}
              increase="-1.3"
              unit="%"
              description={sensorData[sensorData.length - 1].timestamp}
              icon={
                <GrainIcon
                  sx={{ color: theme.palette.secondary[300], fontSize: "26px" }}
                />
              }
            />
          </>
        ) : (
          <p>Loading...</p>
        )}
        <Box
          gridColumn="span 8"
          gridRow="span 2"
          backgroundColor={theme.palette.background.alt}
          p="0rem 0rem 0.5rem 0rem"
          borderRadius="0.55rem"
        >
          <OverviewChart view="sales" isDashboard={true} loc={loc} opt={opt} />
        </Box>
        {sensorData.length > 0 ? (
          <>
            <StatBox
              title="Soil moisture"
              value={sensorData[sensorData.length - 1].soil}
              increase="+5"
              unit="%"
              description={sensorData[sensorData.length - 1].timestamp}
              icon={
                <GrassIcon
                  sx={{ color: theme.palette.secondary[300], fontSize: "26px" }}
                />
              }
            />
            <StatBox
              title="Light intensity"
              value={sensorData[sensorData.length - 1].light}
              increase="+23"
              unit="l"
              description={sensorData[sensorData.length - 1].timestamp}
              icon={
                <Brightness6Icon
                  sx={{ color: theme.palette.secondary[300], fontSize: "26px" }}
                />
              }
            />
          </>
        ) : (
          <p>Loading...</p>
        )}
        {/* ROW 2 */}
        <Box
          gridColumn="span 8"
          gridRow="span 3"
          sx={{
            "& .MuiDataGrid-root": {
              border: "none",
              borderRadius: "5rem",
            },
            "& .MuiDataGrid-cell": {
              borderBottom: "none",
            },
            "& .MuiDataGrid-columnHeaders": {
              backgroundColor: theme.palette.background.alt,
              color: theme.palette.secondary[100],
              borderBottom: "none",
            },
            "& .MuiDataGrid-virtualScroller": {
              backgroundColor: theme.palette.background.alt,
            },
            "& .MuiDataGrid-footerContainer": {
              backgroundColor: theme.palette.background.alt,
              color: theme.palette.secondary[100],
              borderTop: "none",
            },
            "& .MuiDataGrid-toolbarContainer .MuiButton-text": {
              color: `${theme.palette.secondary[200]} !important`,
            },
          }}
        >
          <DataGrid
            loading={!pumpData}
            getRowId={(row) => row._id}
            rows={pumpData || []}
            columns={columns}
          />
        </Box>
        <Box
          gridColumn="span 4"
          gridRow="span 3"
          backgroundColor={theme.palette.background.alt}
          p="0rem"
          borderRadius="0.55rem"
        >
          <Typography
            variant="h6"
            sx={{
              color: theme.palette.secondary[100],
              marginLeft: 3,
              marginTop: 3,
            }}
          >
            Pump Action Stats
          </Typography>
          <BreakdownChart isDashboard={true} loc={loc} />
        </Box>
      </Box>
    </Box>
  );
};

export default Dashboard;
