import React from 'react';
import Box from '@mui/material/Box';
import Typography from '@mui/material/Typography';
import Button from '@mui/material/Button';
import { TCalibrationFormProps } from './CalibrationStepper';

const AuxCalForm = ({ mutation, lampMutation, cal_id, has_data }: TCalibrationFormProps) => {
  return (
    <Box sx={{ mt: 2, padding: 3, border: '1px solid #ddd', borderRadius: 2 }}>
      <Typography variant="h6" gutterBottom>
        Aux + Cal
      </Typography>
      <Typography paragraph>
        Turn off the calibration lamp but do not remove it from the sphere. Turn
        on the auxiliary lamp and allow it to stabilize for 10 minutes.
      </Typography>
      <Button
        variant="contained"
        color="primary"
        onClick={() => lampMutation?.mutate(false)}
      >
        Lamp Off
      </Button>
      <Button
        variant="contained"
        color="primary"
        onClick={() => lampMutation?.mutate(true)}
      >
        Lamp On
      </Button>

      <Button
        variant="contained"
        color="primary"
        onClick={() => mutation?.mutate(cal_id)}
        disabled={
          mutation?.isLoading || mutation?.isSuccess || !lampMutation?.isSuccess || has_data
        }
      >
        Measure Aux + Cal
      </Button>
    </Box>
  );
};

export default AuxCalForm;
