import React from "react";
import { Box, Typography, useTheme } from "@mui/material";
import FlexBetween from "./FlexBetween";

const StatBox = ({ title, value, unit, increase, icon, description }) => {
  const theme = useTheme();
  return (
    <Box
      gridColumn="span 2"
      gridRow="span 1"
      display="flex"
      flexDirection="column"
      justifyContent="space-between"
      p="1.25rem 1rem 1rem 1rem"
      flex="1 1 100%"
      backgroundColor={theme.palette.background.alt}
      borderRadius="0.55rem"
    >
      <Typography variant="h6" sx={{ color: theme.palette.secondary[100] }}>
        {title}
      </Typography>

      <Box
        sx={{
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
          width: '100%',
        }}
      >
        <Box
          sx={{
            display: "flex",
            gap: 1
          }}
        >
          {icon}
          <Typography
            variant="h3"
            fontWeight="600"
            sx={{ color: theme.palette.secondary[200] }}
          >
            {value+unit}
          </Typography>
        </Box>
      </Box>
      <Box sx={{
        display: "flex",
        flexDirection: "column",
        gap: 0.3
      }}>
        <Typography
          variant="h5"
          fontStyle="italic"
          sx={{ color: theme.palette.secondary.light }}
        >
          {increase+unit}
        </Typography>
        <Typography sx={{
          fontSize: '10px',
          fontStyle: "italic",
          marginLeft: 0.5
        }}>Last: {description}</Typography>
      </Box>
    </Box>
  );
};

export default StatBox;
