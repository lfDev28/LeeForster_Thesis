import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { TCalibrationFormProps } from './CalibrationStepper';

const CalForm = ({ mutation, cal_id, has_data }: TCalibrationFormProps) => {
  return (
    <Box sx={{ mt: 2, padding: 3, border: '1px solid #ddd', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Measure Cal
      </Typography>
      <Typography paragraph>
        Turn on the lamp and allow it to stabilize for 10 minutes.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => mutation?.mutate(cal_id)}
        disabled={mutation?.isLoading || mutation?.isSuccess || has_data}
      >
        Measure Cal
      </Button>
    </Box>
  );
};

export default CalForm;
